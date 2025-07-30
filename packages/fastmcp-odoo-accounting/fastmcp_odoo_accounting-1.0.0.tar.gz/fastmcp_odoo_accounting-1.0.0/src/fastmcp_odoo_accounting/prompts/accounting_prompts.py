"""Guided prompts for common Odoo Accounting workflows."""

from typing import List, Dict, Any
from datetime import date, datetime
from fastmcp import Context

from ..server import mcp


@mcp.prompt()
async def financial_overview(ctx: Context) -> str:
    """Get a comprehensive financial overview prompt.
    
    This prompt helps users get a quick snapshot of their financial position.
    """
    today = datetime.now().date()
    month_start = date(today.year, today.month, 1)
    
    return f"""Please provide a financial overview including:

1. **Cash Position**: Show current balances in all bank and cash accounts
2. **Receivables**: List top 5 customers with outstanding balances and any overdue invoices
3. **Payables**: List top 5 vendors with outstanding bills
4. **Monthly Performance**: Show revenue and expenses for the current month (from {month_start} to {today})
5. **Key Metrics**: Calculate current ratio if possible (current assets / current liabilities)

Use the available tools to gather this information and present it in a clear, executive summary format."""


@mcp.prompt()
async def aged_receivables_analysis(ctx: Context) -> str:
    """Analyze aged receivables for collection follow-up.
    
    This prompt helps identify customers requiring collection attention.
    """
    return """Please perform an aged receivables analysis:

1. Generate an aged receivables report showing:
   - Current (not yet due)
   - 1-30 days overdue
   - 31-60 days overdue
   - 61-90 days overdue
   - Over 90 days overdue

2. For each aging bucket, show:
   - Total amount
   - Number of invoices
   - Top 3 customers by amount

3. Highlight any customers with invoices over 60 days overdue

4. Calculate the percentage of total receivables in each aging bucket

This analysis will help prioritize collection efforts."""


@mcp.prompt()
async def monthly_closing_checklist(ctx: Context) -> str:
    """Monthly closing checklist for accountants.
    
    This prompt guides through essential month-end procedures.
    """
    return """Please help me with the monthly closing process by checking:

1. **Unposted Entries**: List any draft journal entries that need to be posted
2. **Bank Reconciliation**: Show any unreconciled payments
3. **Invoice Status**: 
   - List draft customer invoices
   - List draft vendor bills
4. **Account Balances**: Show trial balance for the month
5. **P&L Summary**: Generate a profit & loss statement for the month

For each item found, provide the details and suggested actions."""


@mcp.prompt()
async def customer_statement(ctx: Context, customer_name: str) -> str:
    """Generate a customer statement prompt.
    
    Args:
        customer_name: Name of the customer
    """
    return f"""Please generate a comprehensive statement for customer: {customer_name}

Include:
1. **Customer Details**: Full contact information and credit terms
2. **Account Summary**: 
   - Total outstanding balance
   - Credit limit (if set)
   - Available credit
3. **Open Invoices**: List all unpaid invoices with:
   - Invoice number and date
   - Due date
   - Original amount
   - Amount remaining
   - Days overdue (if applicable)
4. **Recent Payments**: Show payments received in the last 30 days
5. **Aging Summary**: Break down outstanding balance by age

Format this as a professional statement suitable for sending to the customer."""


@mcp.prompt()
async def expense_analysis(ctx: Context, expense_category: str = None) -> str:
    """Analyze expense trends and patterns.
    
    Args:
        expense_category: Optional specific expense category to analyze
    """
    category_text = f" for {expense_category}" if expense_category else ""
    
    return f"""Please perform an expense analysis{category_text}:

1. **Current Month**: Show total expenses{category_text} for the current month
2. **Comparison**: Compare to:
   - Previous month
   - Same month last year (if data available)
3. **Top Expenses**: List top 10 expense accounts by amount
4. **Vendor Analysis**: Show top 5 vendors by total spent
5. **Trends**: Identify any significant increases or decreases

Provide insights on:
- Unusual or unexpected expenses
- Opportunities for cost reduction
- Budget variance (if applicable)"""


@mcp.prompt()
async def cash_flow_forecast(ctx: Context, days_ahead: int = 30) -> str:
    """Create a cash flow forecast prompt.
    
    Args:
        days_ahead: Number of days to forecast (default: 30)
    """
    return f"""Please help create a cash flow forecast for the next {days_ahead} days:

1. **Starting Position**: Current cash and bank balances
2. **Expected Inflows**:
   - Outstanding customer invoices by due date
   - Recurring revenue (if identifiable)
3. **Expected Outflows**:
   - Outstanding vendor bills by due date
   - Recurring expenses (if identifiable)
4. **Daily Projection**: Show expected cash balance for key dates
5. **Analysis**:
   - Identify potential cash shortfalls
   - Highlight largest upcoming payments
   - Suggest actions if cash flow issues detected

Present this as a clear cash flow projection with recommendations."""


@mcp.prompt()
async def audit_trail(ctx: Context, document_number: str) -> str:
    """Trace the complete audit trail for a document.
    
    Args:
        document_number: Invoice, bill, or entry number to trace
    """
    return f"""Please provide a complete audit trail for document: {document_number}

Include:
1. **Document Details**: Full information about the document
2. **Journal Entries**: Show all related journal entries
3. **Account Impact**: List all accounts affected and amounts
4. **Payment History**: Show any payments or reconciliations
5. **Related Documents**: List any related credit notes, refunds, etc.
6. **Timeline**: Create a chronological timeline of all events

This will help trace the complete lifecycle of this transaction."""


@mcp.prompt()
async def tax_summary(ctx: Context, tax_period: str = "current_month") -> str:
    """Generate a tax summary for reporting.
    
    Args:
        tax_period: Period for tax summary (default: current month)
    """
    return f"""Please generate a tax summary for {tax_period}:

1. **Sales Tax**:
   - Total sales subject to tax
   - Tax collected by rate
   - Total tax collected
2. **Purchase Tax**:
   - Total purchases subject to tax
   - Tax paid by rate
   - Total tax paid
3. **Net Position**: Calculate net tax payable/receivable
4. **By Tax Code**: Break down amounts by tax code
5. **Supporting Details**: List key invoices/bills contributing to tax amounts

Note: This is a summary for review. Consult official Odoo tax reports for filing."""