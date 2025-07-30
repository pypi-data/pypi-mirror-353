"""Journal-related tools for Odoo Accounting MCP."""

from typing import List, Optional
from datetime import date as DateType
from fastmcp import Context

from ..server import mcp
from ..models import Journal, JournalEntry, JournalEntryDetailed, JournalEntryLine
from ..auth import require_scope
from ..odoo_connector import OdooUpstreamError, OdooConnectionError


@mcp.tool()
@require_scope("journals:read")
async def list_journals(
    ctx: Context,
    journal_type: Optional[str] = None
) -> List[Journal]:
    """List all accounting journals.
    
    Args:
        journal_type: Filter by type ('sale', 'purchase', 'cash', 'bank', 'general', 'situation')
        
    Returns:
        List of journals
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain
    domain = []
    if journal_type:
        domain.append(('type', '=', journal_type))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'code', 'display_name',
        'type', 'default_account_id', 'company_id',
        'currency_id', 'active'
    ]
    
    try:
        logger.info(f"Listing journals with type: {journal_type}")
        
        records = await odoo.search_read(
            'account.journal',
            domain=domain,
            fields=fields,
            order='code'
        )
        
        return [Journal(**record) for record in records]
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error listing journals: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing journals: {e}")
        raise OdooConnectionError(f"Failed to list journals: {e}")


@mcp.tool()
@require_scope("journals:read")
async def list_journal_entries(
    ctx: Context,
    journal_code: Optional[str] = None,
    date_from: Optional[DateType] = None,
    date_to: Optional[DateType] = None,
    state: Optional[str] = "posted",
    limit: int = 200
) -> List[JournalEntry]:
    """List journal entries with optional filtering.
    
    Args:
        journal_code: Filter by journal code
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        state: Entry state ('draft', 'posted', or None for all)
        limit: Maximum number of results
        
    Returns:
        List of journal entries
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain
    domain = []
    
    if journal_code:
        # First find the journal
        journal_records = await odoo.search_read(
            'account.journal',
            domain=[('code', '=', journal_code)],
            fields=['id'],
            limit=1
        )
        if journal_records:
            domain.append(('journal_id', '=', journal_records[0]['id']))
        else:
            raise ValueError(f"Journal with code {journal_code} not found")
    
    if date_from:
        domain.append(('date', '>=', date_from.isoformat()))
    if date_to:
        domain.append(('date', '<=', date_to.isoformat()))
    if state:
        domain.append(('state', '=', state))
    
    # Fields to retrieve
    fields = [
        'id', 'name', 'display_name', 'date',
        'journal_id', 'state', 'move_type',
        'amount_total', 'amount_residual',
        'partner_id', 'ref', 'narration'
    ]
    
    try:
        logger.info(f"Listing journal entries with domain: {domain}")
        
        records = await odoo.search_read(
            'account.move',
            domain=domain,
            fields=fields,
            limit=limit,
            order='date desc, id desc'
        )
        
        return [JournalEntry(**record) for record in records]
        
    except ValueError as e:
        raise  # Re-raise not found errors
    except OdooUpstreamError as e:
        logger.error(f"Odoo error listing journal entries: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing journal entries: {e}")
        raise OdooConnectionError(f"Failed to list journal entries: {e}")


@mcp.tool()
@require_scope("journals:read")
async def get_journal_entry(
    ctx: Context,
    entry_id: int
) -> JournalEntryDetailed:
    """Get detailed information about a journal entry including its lines.
    
    Args:
        entry_id: The ID of the journal entry
        
    Returns:
        Detailed journal entry with lines
        
    Raises:
        NotFound: If entry doesn't exist
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Fields for the main entry
    entry_fields = [
        'id', 'name', 'display_name', 'date',
        'journal_id', 'state', 'move_type',
        'amount_total', 'amount_residual',
        'partner_id', 'ref', 'narration',
        'currency_id', 'company_id'
    ]
    
    # Fields for the lines
    line_fields = [
        'id', 'name', 'account_id',
        'debit', 'credit', 'balance',
        'partner_id', 'date', 'move_id',
        'tax_ids'
    ]
    
    try:
        logger.info(f"Getting journal entry {entry_id}")
        
        # Get the main entry
        entry_records = await odoo.read(
            'account.move',
            [entry_id],
            fields=entry_fields
        )
        
        if not entry_records:
            raise ValueError(f"Journal entry {entry_id} not found")
        
        entry_data = entry_records[0]
        
        # Get the lines
        line_records = await odoo.search_read(
            'account.move.line',
            domain=[('move_id', '=', entry_id)],
            fields=line_fields,
            order='sequence, id'
        )
        
        # Create line objects
        lines = [JournalEntryLine(**line) for line in line_records]
        
        # Create detailed entry
        return JournalEntryDetailed(
            **entry_data,
            line_ids=lines
        )
        
    except ValueError as e:
        raise  # Re-raise not found errors
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting journal entry {entry_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting journal entry {entry_id}: {e}")
        raise OdooConnectionError(f"Failed to get journal entry: {e}")


@mcp.tool()
@require_scope("journals:read")
async def get_journal_summary(
    ctx: Context,
    journal_code: str,
    date_from: Optional[DateType] = None,
    date_to: Optional[DateType] = None
) -> dict:
    """Get a summary of journal activity for a period.
    
    Args:
        journal_code: The journal code
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        
    Returns:
        Summary with totals and entry counts
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    try:
        # Get journal
        journal_records = await odoo.search_read(
            'account.journal',
            domain=[('code', '=', journal_code)],
            fields=['id', 'name', 'type'],
            limit=1
        )
        
        if not journal_records:
            raise ValueError(f"Journal with code {journal_code} not found")
        
        journal = journal_records[0]
        
        # Build domain for entries
        domain = [
            ('journal_id', '=', journal['id']),
            ('state', '=', 'posted')
        ]
        
        if date_from:
            domain.append(('date', '>=', date_from.isoformat()))
        if date_to:
            domain.append(('date', '<=', date_to.isoformat()))
        
        logger.info(f"Getting summary for journal {journal_code}")
        
        # Get entries
        entries = await odoo.search_read(
            'account.move',
            domain=domain,
            fields=['amount_total', 'move_type']
        )
        
        # Calculate summary
        total_entries = len(entries)
        total_amount = sum(entry['amount_total'] for entry in entries)
        
        # Group by type
        by_type = {}
        for entry in entries:
            move_type = entry['move_type']
            if move_type not in by_type:
                by_type[move_type] = {'count': 0, 'total': 0.0}
            by_type[move_type]['count'] += 1
            by_type[move_type]['total'] += entry['amount_total']
        
        return {
            'journal_code': journal_code,
            'journal_name': journal['name'],
            'journal_type': journal['type'],
            'date_from': date_from.isoformat() if date_from else None,
            'date_to': date_to.isoformat() if date_to else None,
            'total_entries': total_entries,
            'total_amount': total_amount,
            'by_type': by_type
        }
        
    except ValueError as e:
        raise  # Re-raise not found errors
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting journal summary: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting journal summary: {e}")
        raise OdooConnectionError(f"Failed to get journal summary: {e}")