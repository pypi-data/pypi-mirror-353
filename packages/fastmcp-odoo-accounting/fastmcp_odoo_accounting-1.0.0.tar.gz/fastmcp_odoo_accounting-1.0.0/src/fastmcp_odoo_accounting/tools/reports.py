"""Financial reporting tools for Odoo Accounting MCP."""

from typing import List, Dict, Any, Optional
from datetime import date as DateType
from fastmcp import Context

from ..server import mcp
from ..models import TrialBalanceLine, ProfitAndLossReport
from ..auth import require_scope
from ..odoo_connector import OdooUpstreamError, OdooConnectionError


@mcp.tool()
@require_scope("reports:read")
async def get_trial_balance(
    ctx: Context,
    date_from: DateType,
    date_to: DateType,
    target_move: str = "posted"
) -> List[TrialBalanceLine]:
    """Generate a trial balance report for a date range.
    
    Args:
        date_from: Start date
        date_to: End date
        target_move: Include 'posted' entries only or 'all'
        
    Returns:
        List of trial balance lines
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    try:
        logger.info(f"Generating trial balance from {date_from} to {date_to}")
        
        # Build domain for move lines
        domain = [
            ('date', '>=', date_from.isoformat()),
            ('date', '<=', date_to.isoformat())
        ]
        
        if target_move == "posted":
            domain.append(('parent_state', '=', 'posted'))
        
        # Get all accounts with moves in the period
        account_ids = await odoo.search(
            'account.account',
            domain=[],
            order='code'
        )
        
        trial_balance_lines = []
        
        # Process each account
        for account_id in account_ids:
            # Get account details
            account_data = await odoo.read(
                'account.account',
                [account_id],
                fields=['code', 'name']
            )
            
            if not account_data:
                continue
                
            account = account_data[0]
            
            # Get initial balance (before date_from)
            initial_domain = [
                ('account_id', '=', account_id),
                ('date', '<', date_from.isoformat())
            ]
            if target_move == "posted":
                initial_domain.append(('parent_state', '=', 'posted'))
            
            initial_lines = await odoo.search_read(
                'account.move.line',
                domain=initial_domain,
                fields=['debit', 'credit']
            )
            
            initial_debit = sum(line['debit'] for line in initial_lines)
            initial_credit = sum(line['credit'] for line in initial_lines)
            initial_balance = initial_debit - initial_credit
            
            # Get period movements
            period_domain = [
                ('account_id', '=', account_id),
                ('date', '>=', date_from.isoformat()),
                ('date', '<=', date_to.isoformat())
            ]
            if target_move == "posted":
                period_domain.append(('parent_state', '=', 'posted'))
            
            period_lines = await odoo.search_read(
                'account.move.line',
                domain=period_domain,
                fields=['debit', 'credit']
            )
            
            period_debit = sum(line['debit'] for line in period_lines)
            period_credit = sum(line['credit'] for line in period_lines)
            
            # Calculate ending balance
            ending_debit = initial_debit + period_debit
            ending_credit = initial_credit + period_credit
            ending_balance = ending_debit - ending_credit
            
            # Only include accounts with movements
            if initial_balance != 0 or period_debit != 0 or period_credit != 0:
                trial_balance_lines.append(
                    TrialBalanceLine(
                        account_code=account['code'],
                        account_name=account['name'],
                        initial_debit=initial_debit,
                        initial_credit=initial_credit,
                        initial_balance=initial_balance,
                        period_debit=period_debit,
                        period_credit=period_credit,
                        ending_debit=ending_debit,
                        ending_credit=ending_credit,
                        ending_balance=ending_balance
                    )
                )
        
        return trial_balance_lines
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error generating trial balance: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating trial balance: {e}")
        raise OdooConnectionError(f"Failed to generate trial balance: {e}")


@mcp.tool()
@require_scope("reports:read")
async def get_profit_and_loss(
    ctx: Context,
    date_from: DateType,
    date_to: DateType,
    target_move: str = "posted"
) -> ProfitAndLossReport:
    """Generate a profit and loss report for a date range.
    
    Args:
        date_from: Start date
        date_to: End date
        target_move: Include 'posted' entries only or 'all'
        
    Returns:
        Profit and loss report structure
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    try:
        logger.info(f"Generating P&L from {date_from} to {date_to}")
        
        # Build domain for move lines
        domain = [
            ('date', '>=', date_from.isoformat()),
            ('date', '<=', date_to.isoformat())
        ]
        
        if target_move == "posted":
            domain.append(('parent_state', '=', 'posted'))
        
        # Get revenue accounts
        revenue_accounts = await odoo.search_read(
            'account.account',
            domain=[('account_type', 'in', ['income', 'income_other'])],
            fields=['id', 'code', 'name']
        )
        
        # Get expense accounts
        expense_accounts = await odoo.search_read(
            'account.account',
            domain=[('account_type', 'in', ['expense', 'expense_depreciation', 'expense_direct_cost'])],
            fields=['id', 'code', 'name']
        )
        
        # Calculate revenue
        revenue_dict = {}
        total_revenue = 0.0
        
        for account in revenue_accounts:
            account_domain = domain + [('account_id', '=', account['id'])]
            
            lines = await odoo.search_read(
                'account.move.line',
                domain=account_domain,
                fields=['credit', 'debit']
            )
            
            # For income accounts, credit is positive
            account_balance = sum(line['credit'] - line['debit'] for line in lines)
            
            if account_balance != 0:
                key = f"{account['code']} - {account['name']}"
                revenue_dict[key] = account_balance
                total_revenue += account_balance
        
        # Calculate expenses
        expense_dict = {}
        total_expenses = 0.0
        
        for account in expense_accounts:
            account_domain = domain + [('account_id', '=', account['id'])]
            
            lines = await odoo.search_read(
                'account.move.line',
                domain=account_domain,
                fields=['debit', 'credit']
            )
            
            # For expense accounts, debit is positive
            account_balance = sum(line['debit'] - line['credit'] for line in lines)
            
            if account_balance != 0:
                key = f"{account['code']} - {account['name']}"
                expense_dict[key] = account_balance
                total_expenses += account_balance
        
        # Calculate net profit
        net_profit = total_revenue - total_expenses
        
        return ProfitAndLossReport(
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            revenue=revenue_dict,
            expenses=expense_dict,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_profit=net_profit
        )
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error generating P&L: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating P&L: {e}")
        raise OdooConnectionError(f"Failed to generate P&L: {e}")


@mcp.tool()
@require_scope("reports:read")
async def get_aged_receivables(
    ctx: Context,
    as_of_date: DateType = None,
    partner_id: Optional[int] = None
) -> List[dict]:
    """Generate an aged receivables report.
    
    Args:
        as_of_date: Reference date (default: today)
        partner_id: Filter by specific partner
        
    Returns:
        List of aged receivables by partner
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    from datetime import datetime, timedelta
    
    if not as_of_date:
        as_of_date = datetime.now().date()
    
    try:
        logger.info(f"Generating aged receivables as of {as_of_date}")
        
        # Build domain for receivable move lines
        domain = [
            ('account_id.account_type', '=', 'asset_receivable'),
            ('date', '<=', as_of_date.isoformat()),
            ('parent_state', '=', 'posted'),
            ('reconciled', '=', False)  # Only unreconciled
        ]
        
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        
        # Get all receivable lines
        move_lines = await odoo.search_read(
            'account.move.line',
            domain=domain,
            fields=['id', 'partner_id', 'date', 'date_maturity', 'amount_residual', 'move_id']
        )
        
        # Group by partner and age
        partner_aging = {}
        
        for line in move_lines:
            if not line.get('partner_id'):
                continue
                
            partner_id = line['partner_id'][0]
            partner_name = line['partner_id'][1]
            
            if partner_id not in partner_aging:
                partner_aging[partner_id] = {
                    'partner_id': partner_id,
                    'partner_name': partner_name,
                    'current': 0.0,
                    '1-30': 0.0,
                    '31-60': 0.0,
                    '61-90': 0.0,
                    'over_90': 0.0,
                    'total': 0.0
                }
            
            # Determine age bucket
            due_date = datetime.fromisoformat(line.get('date_maturity') or line['date']).date()
            days_overdue = (as_of_date - due_date).days
            amount = line['amount_residual']
            
            if days_overdue <= 0:
                partner_aging[partner_id]['current'] += amount
            elif days_overdue <= 30:
                partner_aging[partner_id]['1-30'] += amount
            elif days_overdue <= 60:
                partner_aging[partner_id]['31-60'] += amount
            elif days_overdue <= 90:
                partner_aging[partner_id]['61-90'] += amount
            else:
                partner_aging[partner_id]['over_90'] += amount
            
            partner_aging[partner_id]['total'] += amount
        
        # Convert to list and sort by total
        results = list(partner_aging.values())
        results.sort(key=lambda x: x['total'], reverse=True)
        
        return results
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error generating aged receivables: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating aged receivables: {e}")
        raise OdooConnectionError(f"Failed to generate aged receivables: {e}")


@mcp.tool()
@require_scope("reports:read")
async def get_cash_flow_summary(
    ctx: Context,
    date_from: DateType,
    date_to: DateType
) -> dict:
    """Generate a cash flow summary for a date range.
    
    Args:
        date_from: Start date
        date_to: End date
        
    Returns:
        Cash flow summary with inflows and outflows
    """
    odoo = ctx.lifespan_context["odoo"]
    logger = ctx.lifespan_context["logger"]
    
    try:
        logger.info(f"Generating cash flow summary from {date_from} to {date_to}")
        
        # Get cash and bank accounts
        cash_accounts = await odoo.search_read(
            'account.account',
            domain=[('account_type', '=', 'asset_cash')],
            fields=['id', 'code', 'name']
        )
        
        cash_account_ids = [acc['id'] for acc in cash_accounts]
        
        if not cash_account_ids:
            return {
                'date_from': date_from.isoformat(),
                'date_to': date_to.isoformat(),
                'opening_balance': 0.0,
                'closing_balance': 0.0,
                'total_inflows': 0.0,
                'total_outflows': 0.0,
                'net_change': 0.0,
                'details': []
            }
        
        # Get opening balance
        opening_lines = await odoo.search_read(
            'account.move.line',
            domain=[
                ('account_id', 'in', cash_account_ids),
                ('date', '<', date_from.isoformat()),
                ('parent_state', '=', 'posted')
            ],
            fields=['debit', 'credit']
        )
        
        opening_balance = sum(line['debit'] - line['credit'] for line in opening_lines)
        
        # Get period movements
        period_lines = await odoo.search_read(
            'account.move.line',
            domain=[
                ('account_id', 'in', cash_account_ids),
                ('date', '>=', date_from.isoformat()),
                ('date', '<=', date_to.isoformat()),
                ('parent_state', '=', 'posted')
            ],
            fields=['date', 'name', 'debit', 'credit', 'partner_id', 'move_id']
        )
        
        # Calculate flows
        total_inflows = 0.0
        total_outflows = 0.0
        details = []
        
        for line in period_lines:
            amount = line['debit'] - line['credit']
            
            if amount > 0:
                total_inflows += amount
                flow_type = 'inflow'
            else:
                total_outflows += abs(amount)
                flow_type = 'outflow'
                amount = abs(amount)
            
            details.append({
                'date': line['date'],
                'description': line['name'],
                'partner': line['partner_id'][1] if line.get('partner_id') else None,
                'amount': amount,
                'type': flow_type
            })
        
        # Sort details by date
        details.sort(key=lambda x: x['date'])
        
        # Calculate closing balance
        net_change = total_inflows - total_outflows
        closing_balance = opening_balance + net_change
        
        return {
            'date_from': date_from.isoformat(),
            'date_to': date_to.isoformat(),
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'total_inflows': total_inflows,
            'total_outflows': total_outflows,
            'net_change': net_change,
            'details': details[:100]  # Limit details to prevent huge responses
        }
        
    except OdooUpstreamError as e:
        logger.error(f"Odoo error generating cash flow: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating cash flow: {e}")
        raise OdooConnectionError(f"Failed to generate cash flow: {e}")