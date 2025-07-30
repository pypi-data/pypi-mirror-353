"""Account-related tools for Odoo Accounting MCP."""

from typing import List, Optional
from datetime import date as DateType
from fastmcp import Context

from ..server import mcp
from ..models import Account, AccountBalance
from ..auth import require_scope
from ..odoo_connector import OdooUpstreamError, OdooConnectionError


@mcp.tool()
@require_scope("accounts:read")
async def list_accounts(
    ctx: Context,
    account_type: Optional[str] = None,
    active_only: bool = True,
    search: Optional[str] = None,
    limit: int = 500
) -> List[Account]:
    """List accounts from the chart of accounts.
    
    Args:
        account_type: Filter by account type (e.g., 'asset_receivable', 'liability_payable')
        active_only: Only show active (non-deprecated) accounts
        search: Search in account code or name
        limit: Maximum number of results
        
    Returns:
        List of accounts matching the criteria
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Build domain
    domain = []
    
    if account_type:
        domain.append(('account_type', '=', account_type))
    
    # Note: 'deprecated' field doesn't exist in Odoo 18
    # TODO: Find alternative way to filter inactive accounts
    if active_only:
        pass  # For now, we can't filter by deprecated status
        
    if search:
        domain.append('|')
        domain.append(('code', 'ilike', search))
        domain.append(('name', 'ilike', search))
    
    # Fields to retrieve
    # Note: 'company_id' field doesn't exist in Odoo 18
    fields = [
        'id', 'code', 'name', 'display_name',
        'account_type', 'internal_group',
        'reconcile'
    ]
    
    try:
        logger.info(f"Listing accounts with domain: {domain}")
        
        records = await odoo.search_read(
            'account.account',
            domain=domain,
            fields=fields,
            limit=limit,
            order='code'
        )
        
        return [Account(**record) for record in records]
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error listing accounts: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing accounts: {e}")
        raise OdooConnectionError(f"Failed to list accounts: {e}")


@mcp.tool()
@require_scope("accounts:read")
async def get_account(
    ctx: Context,
    account_code: str
) -> Account:
    """Get detailed information about a specific account.
    
    Args:
        account_code: The code of the account to retrieve
        
    Returns:
        Detailed account information
        
    Raises:
        NotFound: If account doesn't exist
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    # Search for account by code
    domain = [('code', '=', account_code)]
    
    # Fields to retrieve
    # Note: 'company_id' field doesn't exist in Odoo 18
    fields = [
        'id', 'code', 'name', 'display_name',
        'account_type', 'internal_group',
        'reconcile',
        'currency_id', 'note'
    ]
    
    try:
        logger.info(f"Getting account {account_code}")
        
        records = await odoo.search_read(
            'account.account',
            domain=domain,
            fields=fields,
            limit=1
        )
        
        if not records:
            raise ValueError(f"Account {account_code} not found")
            
        return Account(**records[0])
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting account {account_code}: {e}")
        raise
    except ValueError as e:
        raise  # Re-raise not found errors
    except Exception as e:
        logger.error(f"Unexpected error getting account {account_code}: {e}")
        raise OdooConnectionError(f"Failed to get account: {e}")


@mcp.tool()
@require_scope("accounts:read")
async def get_account_balance(
    ctx: Context,
    account_code: str,
    date_from: Optional[DateType] = None,
    date_to: Optional[DateType] = None
) -> AccountBalance:
    """Get the balance for an account within a date range.
    
    Args:
        account_code: The code of the account
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        
    Returns:
        Account balance information
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    try:
        # First get the account (duplicate logic to avoid calling the decorated function)
        account_records = await odoo.search_read(
            'account.account',
            domain=[('code', '=', account_code)],
            fields=['id', 'code', 'name', 'display_name', 'account_type', 'internal_group', 'reconcile'],
            limit=1
        )
        
        if not account_records:
            raise ValueError(f"Account {account_code} not found")
        
        account = Account(**account_records[0])
        
        # Build domain for move lines
        domain = [
            ('account_id', '=', account.id),
            ('parent_state', '=', 'posted')  # Only posted entries
        ]
        
        if date_from:
            domain.append(('date', '>=', date_from.isoformat()))
        if date_to:
            domain.append(('date', '<=', date_to.isoformat()))
        
        logger.info(f"Getting balance for account {account_code} from {date_from} to {date_to}")
        
        # Get all move lines for this account
        move_lines = await odoo.search_read(
            'account.move.line',
            domain=domain,
            fields=['debit', 'credit', 'balance']
        )
        
        # Calculate totals
        total_debit = sum(line['debit'] for line in move_lines)
        total_credit = sum(line['credit'] for line in move_lines)
        balance = total_debit - total_credit
        
        return AccountBalance(
            account_code=account.code,
            account_name=account.name,
            debit=total_debit,
            credit=total_credit,
            balance=balance,
            date_from=date_from.isoformat() if date_from else None,
            date_to=date_to.isoformat() if date_to else None
        )
        
    except ValueError as e:
        raise  # Re-raise not found errors
    except OdooUpstreamError as e:
        logger.error(f"Odoo error getting account balance: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting account balance: {e}")
        raise OdooConnectionError(f"Failed to get account balance: {e}")


@mcp.tool()
@require_scope("accounts:read")
async def list_account_types(ctx: Context) -> List[dict]:
    """List all available account types in the system.
    
    Returns:
        List of account types with their descriptions
    """
    # Common Odoo account types
    account_types = [
        {"code": "asset_receivable", "name": "Receivable", "category": "Asset"},
        {"code": "asset_cash", "name": "Bank and Cash", "category": "Asset"},
        {"code": "asset_current", "name": "Current Assets", "category": "Asset"},
        {"code": "asset_non_current", "name": "Non-current Assets", "category": "Asset"},
        {"code": "asset_prepayments", "name": "Prepayments", "category": "Asset"},
        {"code": "asset_fixed", "name": "Fixed Assets", "category": "Asset"},
        {"code": "liability_payable", "name": "Payable", "category": "Liability"},
        {"code": "liability_credit_card", "name": "Credit Card", "category": "Liability"},
        {"code": "liability_current", "name": "Current Liabilities", "category": "Liability"},
        {"code": "liability_non_current", "name": "Non-current Liabilities", "category": "Liability"},
        {"code": "equity", "name": "Equity", "category": "Equity"},
        {"code": "equity_unaffected", "name": "Current Year Earnings", "category": "Equity"},
        {"code": "income", "name": "Income", "category": "Income"},
        {"code": "income_other", "name": "Other Income", "category": "Income"},
        {"code": "expense", "name": "Expenses", "category": "Expense"},
        {"code": "expense_depreciation", "name": "Depreciation", "category": "Expense"},
        {"code": "expense_direct_cost", "name": "Cost of Revenue", "category": "Expense"},
        {"code": "off_balance", "name": "Off-Balance Sheet", "category": "Other"}
    ]
    
    return account_types