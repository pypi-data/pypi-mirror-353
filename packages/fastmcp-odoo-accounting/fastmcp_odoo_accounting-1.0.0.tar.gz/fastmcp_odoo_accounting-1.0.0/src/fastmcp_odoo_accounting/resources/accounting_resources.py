"""URI-style resources for Odoo Accounting data."""

import re
from typing import Any, Dict
from fastmcp import Context

from ..server import mcp
from ..odoo_connector import OdooUpstreamError, OdooConnectionError


@mcp.resource("odoo://account.account/{id}")
async def get_account_resource(ctx: Context, id: str) -> Dict[str, Any]:
    """Get an account by ID via URI.
    
    Example: odoo://account.account/42
    """
    odoo = ctx.lifespan_context["odoo"]
    
    try:
        account_id = int(id)
        records = await odoo.read(
            'account.account',
            [account_id],
            fields=['id', 'code', 'name', 'account_type', 'reconcile']
        )
        
        if not records:
            raise ValueError(f"Account {account_id} not found")
            
        return records[0]
        
    except ValueError as e:
        raise
    except Exception as e:
        raise OdooConnectionError(f"Failed to get account: {e}")


@mcp.resource("odoo://res.partner/{id}")
async def get_partner_resource(ctx: Context, id: str) -> Dict[str, Any]:
    """Get a partner by ID via URI.
    
    Example: odoo://res.partner/123
    """
    odoo = ctx.lifespan_context["odoo"]
    
    try:
        partner_id = int(id)
        records = await odoo.read(
            'res.partner',
            [partner_id],
            fields=['id', 'name', 'email', 'phone', 'customer_rank', 'supplier_rank']
        )
        
        if not records:
            raise ValueError(f"Partner {partner_id} not found")
            
        return records[0]
        
    except ValueError as e:
        raise
    except Exception as e:
        raise OdooConnectionError(f"Failed to get partner: {e}")


@mcp.resource("odoo://account.move/{id}")
async def get_move_resource(ctx: Context, id: str) -> Dict[str, Any]:
    """Get an accounting move (invoice/bill/entry) by ID via URI.
    
    Example: odoo://account.move/789
    """
    odoo = ctx.lifespan_context["odoo"]
    
    try:
        move_id = int(id)
        records = await odoo.read(
            'account.move',
            [move_id],
            fields=['id', 'name', 'date', 'state', 'move_type', 'amount_total', 'partner_id']
        )
        
        if not records:
            raise ValueError(f"Move {move_id} not found")
            
        return records[0]
        
    except ValueError as e:
        raise
    except Exception as e:
        raise OdooConnectionError(f"Failed to get move: {e}")


@mcp.resource("odoo://account.journal")
async def list_journals_resource(ctx: Context) -> list:
    """List all journals via URI.
    
    Example: odoo://account.journal
    """
    odoo = ctx.lifespan_context["odoo"]
    
    try:
        records = await odoo.search_read(
            'account.journal',
            domain=[],
            fields=['id', 'name', 'code', 'type'],
            order='code'
        )
        
        return records
        
    except Exception as e:
        raise OdooConnectionError(f"Failed to list journals: {e}")


@mcp.resource("meta://chart_of_accounts")
async def get_chart_of_accounts(ctx: Context) -> Dict[str, Any]:
    """Get the complete chart of accounts structure.
    
    This is a meta-resource that provides a hierarchical view of all accounts.
    Results are cached for 60 seconds to improve performance.
    
    Example: meta://chart_of_accounts
    """
    odoo = ctx.lifespan_context["odoo"]
    
    try:
        # Get all accounts
        accounts = await odoo.search_read(
            'account.account',
            domain=[],  # Note: 'deprecated' field doesn't exist in Odoo 18
            fields=['id', 'code', 'name', 'account_type', 'internal_group'],
            order='code'
        )
        
        # Group by type
        by_type = {}
        for account in accounts:
            acc_type = account.get('account_type', 'other')
            if acc_type not in by_type:
                by_type[acc_type] = []
            by_type[acc_type].append({
                'id': account['id'],
                'code': account['code'],
                'name': account['name']
            })
        
        return {
            'total_accounts': len(accounts),
            'by_type': by_type,
            'types': list(by_type.keys())
        }
        
    except Exception as e:
        raise OdooConnectionError(f"Failed to get chart of accounts: {e}")


@mcp.resource("odoo://account.payment/{id}")
async def get_payment_resource(ctx: Context, id: str) -> Dict[str, Any]:
    """Get a payment by ID via URI.
    
    Example: odoo://account.payment/456
    """
    odoo = ctx.lifespan_context["odoo"]
    
    try:
        payment_id = int(id)
        records = await odoo.read(
            'account.payment',
            [payment_id],
            fields=['id', 'name', 'date', 'amount', 'payment_type', 'state', 'partner_id']
        )
        
        if not records:
            raise ValueError(f"Payment {payment_id} not found")
            
        return records[0]
        
    except ValueError as e:
        raise
    except Exception as e:
        raise OdooConnectionError(f"Failed to get payment: {e}")


# Pattern-based resource for searching
@mcp.resource("search://{model}")
async def search_resource(ctx: Context, model: str) -> list:
    """Search for records in a model.
    
    Note: Query parameters are not supported in this implementation.
    Use the search tools instead for filtered searches.
    """
    odoo = ctx.lifespan_context["odoo"]
    
    # For now, return all records (limited)
    domain = []
    
    # Map model to allowed models
    allowed_models = {
        'res.partner': ['id', 'name', 'email', 'phone'],
        'account.account': ['id', 'code', 'name', 'account_type'],
        'account.journal': ['id', 'code', 'name', 'type'],
        'account.move': ['id', 'name', 'date', 'state', 'partner_id']
    }
    
    if model not in allowed_models:
        raise ValueError(f"Model {model} not allowed for search")
    
    try:
        records = await odoo.search_read(
            model,
            domain=domain,
            fields=allowed_models[model],
            limit=50
        )
        
        return records
        
    except Exception as e:
        raise OdooConnectionError(f"Failed to search {model}: {e}")