"""FastMCP server for Odoo Accounting."""

import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import click
import uvicorn
from fastmcp import FastMCP, Context

from .config import load_config, Config
from .logging_setup import setup_logging
from .odoo_connector import OdooConnector
from .auth import bearer_provider


# Global references for lifespan
_odoo_connector: Optional[OdooConnector] = None
_logger = None


@asynccontextmanager
async def lifespan_ctx(server: FastMCP):
    """Manage server lifecycle - startup and shutdown."""
    global _odoo_connector, _logger
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    _logger = setup_logging(config.log_level)
    _logger.info("Starting Odoo Accounting MCP Server")
    
    # Create and connect Odoo connector
    try:
        _odoo_connector = OdooConnector(config)
        await _odoo_connector.connect()
        _logger.info("Successfully connected to Odoo")
    except Exception as e:
        _logger.error(f"Failed to connect to Odoo: {e}")
        raise
    
    # Yield context to be available in tools
    yield {
        "odoo": _odoo_connector,
        "logger": _logger,
        "config": config
    }
    
    # Shutdown
    _logger.info("Shutting down Odoo Accounting MCP Server")
    if _odoo_connector:
        await _odoo_connector.close()


# Create FastMCP instance
mcp = FastMCP(
    "Odoo-Accounting-ReadOnly",
    instructions="""A safe, read-only gateway to Odoo Accounting data.
    
This server provides comprehensive access to:
- Partners (customers and vendors)
- Chart of Accounts
- Journal entries
- Customer invoices and vendor bills
- Payments
- Financial reports (Trial Balance, P&L)

All operations are strictly read-only for security.""",
    lifespan=lifespan_ctx
)


# Import tools and resources to register them
from . import tools, resources, prompts


@click.group()
def cli():
    """Odoo Accounting MCP Server CLI."""
    pass


@cli.command()
@click.option('--host', default=None, help='Host to bind to')
@click.option('--port', default=None, type=int, help='Port to bind to')
@click.option('--transport', default=None, help='Transport type (streamable-http, sse, stdio)')
def run(host: str, port: int, transport: str):
    """Run the MCP server."""
    config = load_config()
    
    # Override with CLI options if provided
    host = host or config.mcp_host
    port = port or config.mcp_port
    transport = transport or config.mcp_transport
    
    # Configure auth
    auth = bearer_provider(config)
    if auth:
        mcp.auth = auth
    
    if transport == "stdio":
        # Run in stdio mode for local development
        print("Starting in stdio mode...")
        asyncio.run(mcp.run_stdio())
    else:
        # Run HTTP server
        print(f"Starting HTTP server on {host}:{port} with transport: {transport}")
        uvicorn.run(
            mcp.get_asgi_app(transport=transport),
            host=host,
            port=port,
            log_level=config.log_level.lower()
        )


@cli.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"Odoo Accounting MCP Server v{__version__}")


@cli.command()
def test_connection():
    """Test connection to Odoo."""
    import asyncio
    
    async def _test():
        config = load_config()
        logger = setup_logging(config.log_level)
        
        logger.info("Testing Odoo connection...")
        
        try:
            async with OdooConnector(config) as odoo:
                # Try to read one partner
                partners = await odoo.search_read(
                    'res.partner',
                    domain=[],
                    fields=['id', 'name'],
                    limit=1
                )
                
                if partners:
                    logger.info(f"✓ Connection successful! Found partner: {partners[0]['name']}")
                else:
                    logger.info("✓ Connection successful! (No partners found)")
                    
        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            sys.exit(1)
    
    asyncio.run(_test())


if __name__ == "__main__":
    cli()