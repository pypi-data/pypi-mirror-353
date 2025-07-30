"""Invoice-related tools for Odoo Accounting MCP."""

from typing import List, Optional
from datetime import date as DateType
from fastmcp import Context

from ..server import mcp
from ..models import Invoice, InvoiceDetailed, InvoiceLine
from ..auth import require_scope
from ..odoo_connector import OdooUpstreamError, OdooConnectionError


@mcp.tool()
@require_scope("invoices:read")
async def list_customer_invoices(
    ctx: Context,
    status: Optional[str] = None,
    date_from: Optional[DateType] = None,
    date_to: Optional[DateType] = None,
    customer_name: Optional[str] = None,
    min_amount: Optional[float] = None,
    limit: int = 100
) -> List[Invoice]:
    """List customer invoices with optional filtering.
    
    Args:
        status: Filter by status ('draft', 'posted', 'cancel')
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        customer_name: Filter by customer name (partial match)
        min_amount: Minimum invoice amount
        limit: Maximum number of results
        
    Returns:
        List of customer invoices
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain - only customer invoices
    domain = [('move_type', 'in', ['out_invoice', 'out_refund'])]
    
    if status:
        domain.append(('state', '=', status))
    
    if date_from:
        domain.append(('invoice_date', '>=', date_from.isoformat()))
    if date_to:
        domain.append(('invoice_date', '<=', date_to.isoformat()))
        
    if customer_name:
        # Search for partners first
        partner_ids = await odoo.search(
            'res.partner',
            domain=[('name', 'ilike', customer_name)],
            limit=100
        )
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))
        else:
            return []  # No matching partners
    
    if min_amount is not None:
        domain.append(('amount_total', '>=', min_amount))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'display_name', 'date', 'invoice_date',
        'invoice_date_due', 'partner_id', 'state', 'move_type',
        'amount_total', 'amount_residual', 'payment_state',
        'currency_id', 'invoice_origin', 'ref', 'journal_id'
    ]
    
    try:
        logger.info(f"Listing customer invoices with domain: {domain}")
        
        records = await odoo.search_read(
            'account.move',
            domain=domain,
            fields=fields,
            limit=limit,
            order='invoice_date desc, id desc'
        )
        
        return [Invoice(**record) for record in records]
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error listing customer invoices: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing customer invoices: {e}")
        raise OdooConnectionError(f"Failed to list customer invoices: {e}")


@mcp.tool()
@require_scope("invoices:read")
async def list_vendor_bills(
    ctx: Context,
    status: Optional[str] = None,
    date_from: Optional[DateType] = None,
    date_to: Optional[DateType] = None,
    vendor_name: Optional[str] = None,
    min_amount: Optional[float] = None,
    limit: int = 100
) -> List[Invoice]:
    """List vendor bills with optional filtering.
    
    Args:
        status: Filter by status ('draft', 'posted', 'cancel')
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        vendor_name: Filter by vendor name (partial match)
        min_amount: Minimum bill amount
        limit: Maximum number of results
        
    Returns:
        List of vendor bills
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain - only vendor bills
    domain = [('move_type', 'in', ['in_invoice', 'in_refund'])]
    
    if status:
        domain.append(('state', '=', status))
    
    if date_from:
        domain.append(('invoice_date', '>=', date_from.isoformat()))
    if date_to:
        domain.append(('invoice_date', '<=', date_to.isoformat()))
        
    if vendor_name:
        # Search for partners first
        partner_ids = await odoo.search(
            'res.partner',
            domain=[('name', 'ilike', vendor_name)],
            limit=100
        )
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))
        else:
            return []  # No matching partners
    
    if min_amount is not None:
        domain.append(('amount_total', '>=', min_amount))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'display_name', 'date', 'invoice_date',
        'invoice_date_due', 'partner_id', 'state', 'move_type',
        'amount_total', 'amount_residual', 'payment_state',
        'currency_id', 'invoice_origin', 'ref', 'journal_id'
    ]
    
    try:
        logger.info(f"Listing vendor bills with domain: {domain}")
        
        records = await odoo.search_read(
            'account.move',
            domain=domain,
            fields=fields,
            limit=limit,
            order='invoice_date desc, id desc'
        )
        
        return [Invoice(**record) for record in records]
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error listing vendor bills: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing vendor bills: {e}")
        raise OdooConnectionError(f"Failed to list vendor bills: {e}")


@mcp.tool()
@require_scope("invoices:read")
async def get_invoice(
    ctx: Context,
    invoice_id: int
) -> InvoiceDetailed:
    """Get detailed information about an invoice including its lines.
    
    Args:
        invoice_id: The ID of the invoice
        
    Returns:
        Detailed invoice with lines
        
    Raises:
        NotFound: If invoice doesn't exist
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Fields for the main invoice
    invoice_fields = [
        'id', 'name', 'display_name', 'date', 'invoice_date',
        'invoice_date_due', 'partner_id', 'state', 'move_type',
        'amount_total', 'amount_residual', 'amount_untaxed',
        'amount_tax', 'payment_state', 'currency_id',
        'invoice_origin', 'ref', 'narration',
        'invoice_payment_term_id', 'fiscal_position_id'
    ]
    
    # Fields for the lines
    line_fields = [
        'id', 'name', 'product_id', 'account_id',
        'quantity', 'price_unit', 'discount',
        'price_subtotal', 'price_total',
        'tax_ids'
    ]
    
    try:
        logger.info(f"Getting invoice {invoice_id}")
        
        # Get the main invoice
        invoice_records = await odoo.read(
            'account.move',
            [invoice_id],
            fields=invoice_fields
        )
        
        if not invoice_records:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        invoice_data = invoice_records[0]
        
        # Check if it's actually an invoice
        if invoice_data['move_type'] not in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
            raise ValueError(f"Record {invoice_id} is not an invoice")
        
        # Get the invoice lines (not accounting lines)
        line_records = await odoo.search_read(
            'account.move.line',
            domain=[
                ('move_id', '=', invoice_id),
                ('display_type', 'in', ['product', False])  # Only product lines
            ],
            fields=line_fields,
            order='sequence, id'
        )
        
        # Create line objects
        lines = [InvoiceLine(**line) for line in line_records]
        
        # Create detailed invoice
        return InvoiceDetailed(
            **invoice_data,
            invoice_line_ids=lines
        )
        
    except ValueError as e:
        raise  # Re-raise not found errors
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting invoice {invoice_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting invoice {invoice_id}: {e}")
        raise OdooConnectionError(f"Failed to get invoice: {e}")


@mcp.tool()
@require_scope("invoices:read")
async def get_overdue_invoices(
    ctx: Context,
    days_overdue: int = 1,
    customer_only: bool = True,
    limit: int = 100
) -> List[dict]:
    """Get invoices that are overdue by a certain number of days.
    
    Args:
        days_overdue: Minimum days overdue (default: 1)
        customer_only: Only show customer invoices (default: True)
        limit: Maximum number of results
        
    Returns:
        List of overdue invoices with aging information
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    from datetime import datetime, timedelta
    
    # Calculate cutoff date
    cutoff_date = (datetime.now().date() - timedelta(days=days_overdue)).isoformat()
    
    # Build domain
    domain = [
        ('state', '=', 'posted'),
        ('payment_state', 'in', ['not_paid', 'partial']),
        ('invoice_date_due', '<', cutoff_date)
    ]
    
    if customer_only:
        domain.append(('move_type', 'in', ['out_invoice', 'out_refund']))
    else:
        domain.append(('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'partner_id', 'invoice_date', 'invoice_date_due',
        'amount_total', 'amount_residual', 'currency_id', 'move_type'
    ]
    
    try:
        logger.info(f"Getting overdue invoices (>{days_overdue} days)")
        
        records = await odoo.search_read(
            'account.move',
            domain=domain,
            fields=fields,
            limit=limit,
            order='invoice_date_due'
        )
        
        # Calculate days overdue for each invoice
        today = datetime.now().date()
        results = []
        
        for record in records:
            due_date = datetime.fromisoformat(record['invoice_date_due']).date()
            days_past_due = (today - due_date).days
            
            results.append({
                'id': record['id'],
                'number': record['name'],
                'partner': record['partner_id'][1] if record['partner_id'] else 'Unknown',
                'invoice_date': record['invoice_date'],
                'due_date': record['invoice_date_due'],
                'days_overdue': days_past_due,
                'total_amount': record['amount_total'],
                'amount_due': record['amount_residual'],
                'currency': record['currency_id'][1] if record['currency_id'] else 'Unknown',
                'type': record['move_type']
            })
        
        return results
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting overdue invoices: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting overdue invoices: {e}")
        raise OdooConnectionError(f"Failed to get overdue invoices: {e}")