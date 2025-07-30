"""Asynchronous Odoo XML-RPC connector with resilience and error handling."""

import asyncio
import xmlrpc.client
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager
import time
import logging
from functools import wraps

from .config import Config


class OdooError(Exception):
    """Base exception for Odoo-related errors."""
    pass


class OdooAuthenticationError(OdooError):
    """Raised when authentication with Odoo fails."""
    pass


class OdooConnectionError(OdooError):
    """Raised when connection to Odoo fails."""
    pass


class OdooUpstreamError(OdooError):
    """Raised when Odoo returns an error."""
    pass


def with_retry(max_attempts: int = 3, backoff_factor: float = 1.0):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(self, *args, **kwargs)
                except (OdooConnectionError, xmlrpc.client.ProtocolError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor * (2 ** attempt)
                        self.logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        self.logger.error(f"All {max_attempts} attempts failed")
            raise last_error
        return wrapper
    return decorator


class OdooConnector:
    """Asynchronous connector for Odoo XML-RPC API."""
    
    def __init__(self, config: Config, executor: Optional[ThreadPoolExecutor] = None):
        """Initialize the Odoo connector."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.executor = executor or ThreadPoolExecutor(max_workers=10)
        
        # Connection state
        self._uid: Optional[int] = None
        self._models_proxy: Optional[xmlrpc.client.ServerProxy] = None
        self._common_proxy: Optional[xmlrpc.client.ServerProxy] = None
        
        # Connection URLs
        self._common_url = f"{config.odoo_url}/xmlrpc/2/common"
        self._models_url = f"{config.odoo_url}/xmlrpc/2/object"
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def connect(self) -> None:
        """Establish connection and authenticate with Odoo."""
        try:
            # Create XML-RPC proxies
            self._common_proxy = xmlrpc.client.ServerProxy(
                self._common_url,
                allow_none=True
            )
            self._models_proxy = xmlrpc.client.ServerProxy(
                self._models_url,
                allow_none=True
            )
            
            # Authenticate
            self._uid = await self._authenticate()
            self.logger.info("Successfully connected to Odoo")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Odoo: {e}")
            raise OdooConnectionError(f"Failed to connect to Odoo: {e}")
    
    async def close(self) -> None:
        """Close connections and cleanup resources."""
        self._uid = None
        self._models_proxy = None
        self._common_proxy = None
        self.logger.info("Closed Odoo connection")
        
    async def _authenticate(self) -> int:
        """Authenticate with Odoo and return user ID."""
        try:
            uid = await self._run_in_executor(
                self._common_proxy.authenticate,
                self.config.odoo_db,
                self.config.odoo_user,
                self.config.odoo_api_key,
                {}
            )
            
            if not uid:
                raise OdooAuthenticationError("Authentication failed - invalid credentials")
                
            self.logger.info(f"Authenticated as user ID: {uid}")
            return uid
            
        except xmlrpc.client.Fault as e:
            raise OdooAuthenticationError(f"Authentication failed: {e.faultString}")
        except Exception as e:
            raise OdooConnectionError(f"Connection failed during authentication: {e}")
    
    async def _run_in_executor(self, func, *args) -> Any:
        """Run a blocking function in the thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
    
    def _ensure_connected(self) -> None:
        """Ensure we have an active connection."""
        if not self._uid or not self._models_proxy:
            raise OdooConnectionError("Not connected to Odoo. Call connect() first.")
    
    @with_retry(max_attempts=3, backoff_factor=0.5)
    async def search_read(
        self,
        model: str,
        domain: List[List[Any]] = None,
        fields: List[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search and read records from Odoo."""
        self._ensure_connected()
        
        domain = domain or []
        fields = fields or []
        
        try:
            start_time = time.time()
            
            result = await self._run_in_executor(
                self._models_proxy.execute_kw,
                self.config.odoo_db,
                self._uid,
                self.config.odoo_api_key,
                model,
                'search_read',
                [domain],
                {
                    'fields': fields,
                    'limit': limit,
                    'offset': offset,
                    'order': order
                }
            )
            
            duration = time.time() - start_time
            self.logger.debug(
                f"search_read({model}) completed in {duration:.2f}s, "
                f"returned {len(result)} records"
            )
            
            return result
            
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Odoo fault in search_read: {e.faultString}")
            raise OdooUpstreamError(f"Odoo error: {e.faultString}")
        except Exception as e:
            self.logger.error(f"Error in search_read: {e}")
            raise OdooConnectionError(f"Connection error: {e}")
    
    @with_retry(max_attempts=3, backoff_factor=0.5)
    async def read(
        self,
        model: str,
        ids: List[int],
        fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Read specific records by ID."""
        self._ensure_connected()
        
        fields = fields or []
        
        try:
            result = await self._run_in_executor(
                self._models_proxy.execute_kw,
                self.config.odoo_db,
                self._uid,
                self.config.odoo_api_key,
                model,
                'read',
                [ids],
                {'fields': fields} if fields else {}
            )
            
            return result
            
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Odoo fault in read: {e.faultString}")
            raise OdooUpstreamError(f"Odoo error: {e.faultString}")
        except Exception as e:
            self.logger.error(f"Error in read: {e}")
            raise OdooConnectionError(f"Connection error: {e}")
    
    @with_retry(max_attempts=3, backoff_factor=0.5)
    async def search(
        self,
        model: str,
        domain: List[List[Any]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order: Optional[str] = None
    ) -> List[int]:
        """Search for record IDs matching criteria."""
        self._ensure_connected()
        
        domain = domain or []
        
        try:
            result = await self._run_in_executor(
                self._models_proxy.execute_kw,
                self.config.odoo_db,
                self._uid,
                self.config.odoo_api_key,
                model,
                'search',
                [domain],
                {
                    'limit': limit,
                    'offset': offset,
                    'order': order
                }
            )
            
            return result
            
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Odoo fault in search: {e.faultString}")
            raise OdooUpstreamError(f"Odoo error: {e.faultString}")
        except Exception as e:
            self.logger.error(f"Error in search: {e}")
            raise OdooConnectionError(f"Connection error: {e}")
    
    @with_retry(max_attempts=3, backoff_factor=0.5)
    async def search_count(
        self,
        model: str,
        domain: List[List[Any]] = None
    ) -> int:
        """Count records matching criteria."""
        self._ensure_connected()
        
        domain = domain or []
        
        try:
            result = await self._run_in_executor(
                self._models_proxy.execute_kw,
                self.config.odoo_db,
                self._uid,
                self.config.odoo_api_key,
                model,
                'search_count',
                [domain]
            )
            
            return result
            
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Odoo fault in search_count: {e.faultString}")
            raise OdooUpstreamError(f"Odoo error: {e.faultString}")
        except Exception as e:
            self.logger.error(f"Error in search_count: {e}")
            raise OdooConnectionError(f"Connection error: {e}")
    
    async def check_access_rights(
        self,
        model: str,
        operation: str = "read",
        raise_exception: bool = False
    ) -> bool:
        """Check if user has access rights for model and operation."""
        self._ensure_connected()
        
        try:
            result = await self._run_in_executor(
                self._models_proxy.execute_kw,
                self.config.odoo_db,
                self._uid,
                self.config.odoo_api_key,
                model,
                'check_access_rights',
                [operation],
                {'raise_exception': raise_exception}
            )
            
            return result
            
        except xmlrpc.client.Fault as e:
            if raise_exception:
                raise OdooUpstreamError(f"Access denied: {e.faultString}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking access rights: {e}")
            raise OdooConnectionError(f"Connection error: {e}")