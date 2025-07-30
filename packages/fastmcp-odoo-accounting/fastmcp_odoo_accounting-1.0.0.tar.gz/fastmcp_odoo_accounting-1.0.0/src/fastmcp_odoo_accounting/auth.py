"""Authentication utilities for the MCP server."""

import base64
import logging
from typing import Optional

from fastmcp.server.auth import BearerAuthProvider
from .config import Config


logger = logging.getLogger(__name__)


def bearer_provider(config: Optional[Config] = None) -> Optional[BearerAuthProvider]:
    """Create a bearer auth provider if JWT configuration is present."""
    if not config:
        from .config import load_config
        config = load_config()
    
    if not config.jwt_public_key_pem:
        logger.warning(
            "\n" + "="*60 + "\n" +
            "WARNING: Running in DEVELOPMENT MODE - No authentication!\n" +
            "Set JWT_PUBLIC_KEY_PEM for production use.\n" +
            "="*60 + "\n"
        )
        return None
    
    try:
        # Decode base64-encoded PEM key
        public_key = base64.b64decode(config.jwt_public_key_pem).decode('utf-8')
        
        return BearerAuthProvider(
            public_key_pem=public_key,
            iss=config.jwt_issuer,
            aud=config.jwt_audience,
            algorithms=["RS256"]
        )
    except Exception as e:
        logger.error(f"Failed to create auth provider: {e}")
        raise


def require_scope(required_scope: str):
    """Decorator to enforce scope-based access control on tools."""
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            # In development mode (no auth), allow all
            if not hasattr(ctx, 'auth_context'):
                return await func(ctx, *args, **kwargs)
            
            # Check if required scope is present
            token_scopes = ctx.auth_context.get('scope', '').split()
            if required_scope not in token_scopes:
                raise PermissionError(
                    f"Access denied. Required scope '{required_scope}' not found in token."
                )
            
            return await func(ctx, *args, **kwargs)
        
        return wrapper
    
    return decorator