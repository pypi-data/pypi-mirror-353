"""Partner-related tools for Odoo Accounting MCP."""

from typing import List, Optional
from fastmcp import Context

from ..server import mcp
from ..models import Partner
from ..auth import require_scope
from ..odoo_connector import OdooUpstreamError, OdooConnectionError


@mcp.tool()
@require_scope("partners:read")
async def list_partners(
    ctx: Context,
    search: Optional[str] = None,
    is_customer: Optional[bool] = None,
    is_vendor: Optional[bool] = None,
    limit: int = 100
) -> List[Partner]:
    """List partners (customers/vendors) with optional filtering.
    
    Args:
        search: Search in partner name, email, or VAT
        is_customer: Filter for customers only
        is_vendor: Filter for vendors only  
        limit: Maximum number of results (default: 100)
        
    Returns:
        List of partners matching the criteria
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain
    domain = []
    
    if search:
        domain.append('|')
        domain.append('|')
        domain.append(('name', 'ilike', search))
        domain.append(('email', 'ilike', search))
        domain.append(('vat', 'ilike', search))
    
    if is_customer is True:
        domain.append(('customer_rank', '>', 0))
    elif is_customer is False:
        domain.append(('customer_rank', '=', 0))
        
    if is_vendor is True:
        domain.append(('supplier_rank', '>', 0))
    elif is_vendor is False:
        domain.append(('supplier_rank', '=', 0))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'display_name', 'is_company',
        'customer_rank', 'supplier_rank',
        'email', 'phone', 'street', 'city', 'country_id',
        'vat', 'credit', 'debit'
    ]
    
    try:
        logger.info(f"Listing partners with domain: {domain}")
        
        records = await odoo.search_read(
            'res.partner',
            domain=domain,
            fields=fields,
            limit=limit,
            order='name'
        )
        
        return [Partner(**record) for record in records]
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error listing partners: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing partners: {e}")
        raise OdooConnectionError(f"Failed to list partners: {e}")


@mcp.tool()
@require_scope("partners:read")
async def get_partner(
    ctx: Context,
    partner_id: int
) -> Partner:
    """Get detailed information about a specific partner.
    
    Args:
        partner_id: The ID of the partner to retrieve
        
    Returns:
        Detailed partner information
        
    Raises:
        NotFound: If partner doesn't exist
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Fields to retrieve
    # Note: 'mobile' field doesn't exist in Odoo 18
    fields = [
        'id', 'name', 'display_name', 'is_company',
        'customer_rank', 'supplier_rank',
        'email', 'phone', 'website',
        'street', 'street2', 'city', 'state_id', 'zip', 'country_id',
        'vat', 'credit', 'debit', 'credit_limit',
        'property_payment_term_id', 'property_supplier_payment_term_id',
        'property_account_receivable_id', 'property_account_payable_id',
        'comment', 'active'
    ]
    
    try:
        logger.info(f"Getting partner {partner_id}")
        
        records = await odoo.read(
            'res.partner',
            [partner_id],
            fields=fields
        )
        
        if not records:
            raise ValueError(f"Partner {partner_id} not found")
            
        return Partner(**records[0])
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting partner {partner_id}: {e}")
        raise
    except ValueError as e:
        raise  # Re-raise not found errors
    except Exception as e:
        logger.error(f"Unexpected error getting partner {partner_id}: {e}")
        raise OdooConnectionError(f"Failed to get partner: {e}")


@mcp.tool() 
@require_scope("partners:read")
async def get_partner_balance(
    ctx: Context,
    partner_id: int
) -> dict:
    """Get the current balance for a partner.
    
    Args:
        partner_id: The ID of the partner
        
    Returns:
        Dictionary with receivable, payable, and net balance
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    try:
        logger.info(f"Getting balance for partner {partner_id}")
        
        # Get partner with balance fields
        records = await odoo.read(
            'res.partner',
            [partner_id],
            fields=['name', 'credit', 'debit']
        )
        
        if not records:
            raise ValueError(f"Partner {partner_id} not found")
        
        partner = records[0]
        
        return {
            "partner_id": partner_id,
            "partner_name": partner['name'],
            "receivable": partner['debit'],  # Amount we owe to partner
            "payable": partner['credit'],    # Amount partner owes us  
            "net_balance": partner['credit'] - partner['debit']
        }
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting partner balance: {e}")
        raise
    except ValueError as e:
        raise  # Re-raise not found errors
    except Exception as e:
        logger.error(f"Unexpected error getting partner balance: {e}")
        raise OdooConnectionError(f"Failed to get partner balance: {e}")