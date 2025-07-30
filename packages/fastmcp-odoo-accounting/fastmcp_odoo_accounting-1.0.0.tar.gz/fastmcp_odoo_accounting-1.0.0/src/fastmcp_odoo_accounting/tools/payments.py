"""Payment-related tools for Odoo Accounting MCP."""

from typing import List, Optional
from datetime import date as DateType
from fastmcp import Context

from ..server import mcp
from ..models import Payment
from ..auth import require_scope
from ..odoo_connector import OdooUpstreamError, OdooConnectionError


@mcp.tool()
@require_scope("payments:read")
async def list_payments(
    ctx: Context,
    payment_type: Optional[str] = None,
    date_from: Optional[DateType] = None,
    date_to: Optional[DateType] = None,
    partner_name: Optional[str] = None,
    state: Optional[str] = "posted",
    limit: int = 100
) -> List[Payment]:
    """List payments with optional filtering.
    
    Args:
        payment_type: Filter by type ('inbound' for customer payments, 'outbound' for vendor payments)
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        partner_name: Filter by partner name (partial match)
        state: Payment state ('draft', 'posted', 'sent', 'reconciled', 'cancelled')
        limit: Maximum number of results
        
    Returns:
        List of payments
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain
    domain = []
    
    if payment_type:
        domain.append(('payment_type', '=', payment_type))
    
    if date_from:
        domain.append(('date', '>=', date_from.isoformat()))
    if date_to:
        domain.append(('date', '<=', date_to.isoformat()))
        
    if partner_name:
        # Search for partners first
        partner_ids = await odoo.search(
            'res.partner',
            domain=[('name', 'ilike', partner_name)],
            limit=100
        )
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))
        else:
            return []  # No matching partners
    
    if state:
        domain.append(('state', '=', state))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'display_name', 'date',
        'amount', 'payment_type', 'partner_type',
        'partner_id', 'journal_id', 'state',
        'currency_id', 'payment_method_line_id',
        'is_reconciled', 'is_matched'
    ]
    
    try:
        logger.info(f"Listing payments with domain: {domain}")
        
        records = await odoo.search_read(
            'account.payment',
            domain=domain,
            fields=fields,
            limit=limit,
            order='date desc, id desc'
        )
        
        # Map fields to our model
        payments = []
        for record in records:
            # Extract payment date from 'date' field
            payment_data = {
                **record,
                'payment_date': record['date'],
                'payment_method_id': record.get('payment_method_line_id', [None, None])
            }
            payments.append(Payment(**payment_data))
        
        return payments
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error listing payments: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing payments: {e}")
        raise OdooConnectionError(f"Failed to list payments: {e}")


@mcp.tool()
@require_scope("payments:read")
async def get_payment(
    ctx: Context,
    payment_id: int
) -> dict:
    """Get detailed information about a payment including reconciled items.
    
    Args:
        payment_id: The ID of the payment
        
    Returns:
        Detailed payment information with reconciliation details
        
    Raises:
        NotFound: If payment doesn't exist
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Fields for the payment
    payment_fields = [
        'id', 'name', 'display_name', 'date',
        'amount', 'payment_type', 'partner_type',
        'partner_id', 'journal_id', 'state',
        'currency_id', 'payment_method_line_id',
        'is_reconciled', 'is_matched',
        'move_id', 'paired_internal_transfer_payment_id'
    ]
    
    try:
        logger.info(f"Getting payment {payment_id}")
        
        # Get the payment
        payment_records = await odoo.read(
            'account.payment',
            [payment_id],
            fields=payment_fields
        )
        
        if not payment_records:
            raise ValueError(f"Payment {payment_id} not found")
        
        payment_data = payment_records[0]
        
        # Get reconciled items if payment is reconciled
        reconciled_items = []
        if payment_data.get('is_reconciled'):
            # Get the payment's journal entry
            if payment_data.get('move_id'):
                move_id = payment_data['move_id'][0]
                
                # Get move lines for this payment
                move_lines = await odoo.search_read(
                    'account.move.line',
                    domain=[
                        ('move_id', '=', move_id),
                        ('account_id.reconcile', '=', True)
                    ],
                    fields=['id', 'matched_debit_ids', 'matched_credit_ids']
                )
                
                # Get reconciliation details
                for line in move_lines:
                    # Get matched items
                    if line.get('matched_debit_ids') or line.get('matched_credit_ids'):
                        match_ids = line.get('matched_debit_ids', []) + line.get('matched_credit_ids', [])
                        
                        if match_ids:
                            matches = await odoo.read(
                                'account.partial.reconcile',
                                match_ids,
                                fields=['debit_move_id', 'credit_move_id', 'amount']
                            )
                            
                            for match in matches:
                                # Get the other side of the reconciliation
                                other_line_id = match['debit_move_id'][0] if match['credit_move_id'][0] == line['id'] else match['credit_move_id'][0]
                                
                                other_lines = await odoo.read(
                                    'account.move.line',
                                    [other_line_id],
                                    fields=['move_id', 'name', 'date']
                                )
                                
                                if other_lines:
                                    other_line = other_lines[0]
                                    # Get the move details
                                    moves = await odoo.read(
                                        'account.move',
                                        [other_line['move_id'][0]],
                                        fields=['name', 'move_type', 'amount_total']
                                    )
                                    
                                    if moves:
                                        move = moves[0]
                                        reconciled_items.append({
                                            'document': move['name'],
                                            'type': move['move_type'],
                                            'amount': match['amount'],
                                            'date': other_line['date']
                                        })
        
        # Build result
        result = {
            'id': payment_data['id'],
            'name': payment_data['name'],
            'payment_date': payment_data['date'],
            'amount': payment_data['amount'],
            'payment_type': payment_data['payment_type'],
            'partner_type': payment_data['partner_type'],
            'partner': payment_data['partner_id'][1] if payment_data.get('partner_id') else None,
            'journal': payment_data['journal_id'][1] if payment_data.get('journal_id') else None,
            'state': payment_data['state'],
            'currency': payment_data['currency_id'][1] if payment_data.get('currency_id') else None,
            'payment_method': payment_data['payment_method_line_id'][1] if payment_data.get('payment_method_line_id') else None,
            'reference': None,  # ref field doesn't exist in account.payment
            'is_reconciled': payment_data.get('is_reconciled', False),
            'reconciled_items': reconciled_items
        }
        
        return result
        
    except ValueError as e:
        raise  # Re-raise not found errors
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting payment {payment_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting payment {payment_id}: {e}")
        raise OdooConnectionError(f"Failed to get payment: {e}")


@mcp.tool()
@require_scope("payments:read")
async def get_unreconciled_payments(
    ctx: Context,
    partner_id: Optional[int] = None,
    payment_type: Optional[str] = None,
    limit: int = 100
) -> List[dict]:
    """Get payments that haven't been fully reconciled.
    
    Args:
        partner_id: Filter by partner ID
        payment_type: Filter by type ('inbound' or 'outbound')
        limit: Maximum number of results
        
    Returns:
        List of unreconciled payments
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain
    domain = [
        ('state', '=', 'posted'),
        ('is_reconciled', '=', False)
    ]
    
    if partner_id:
        domain.append(('partner_id', '=', partner_id))
    
    if payment_type:
        domain.append(('payment_type', '=', payment_type))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'date', 'amount',
        'payment_type', 'partner_id',
        'journal_id', 'currency_id'
    ]
    
    try:
        logger.info(f"Getting unreconciled payments")
        
        records = await odoo.search_read(
            'account.payment',
            domain=domain,
            fields=fields,
            limit=limit,
            order='date desc'
        )
        
        # Format results
        results = []
        for record in records:
            results.append({
                'id': record['id'],
                'name': record['name'],
                'payment_date': record['date'],
                'amount': record['amount'],
                'payment_type': record['payment_type'],
                'partner': record['partner_id'][1] if record.get('partner_id') else 'Unknown',
                'journal': record['journal_id'][1] if record.get('journal_id') else 'Unknown',
                'currency': record['currency_id'][1] if record.get('currency_id') else 'Unknown'
            })
        
        return results
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting unreconciled payments: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting unreconciled payments: {e}")
        raise OdooConnectionError(f"Failed to get unreconciled payments: {e}")