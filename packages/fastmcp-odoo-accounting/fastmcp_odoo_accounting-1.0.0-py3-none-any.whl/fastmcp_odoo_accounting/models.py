"""Pydantic models for Odoo Accounting data structures."""

from datetime import date as DateType, datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator


# Base models
class OdooModel(BaseModel):
    """Base model for all Odoo records."""
    id: int = Field(..., description="Record ID")
    display_name: str = Field(..., description="Display name")
    
    model_config = {"extra": "allow"}  # Allow extra fields from Odoo


# Partner models
class Partner(OdooModel):
    """Represents a partner (customer/vendor) in Odoo."""
    name: str = Field(..., description="Partner name")
    is_company: bool = Field(default=False, description="Is a company")
    customer_rank: int = Field(default=0, description="Customer rank")
    supplier_rank: int = Field(default=0, description="Supplier rank")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    country_id: Optional[List[Any]] = Field(None, description="Country")
    vat: Optional[str] = Field(None, description="VAT number")
    credit: float = Field(default=0.0, description="Total receivable")
    debit: float = Field(default=0.0, description="Total payable")
    
    @field_validator('email', 'phone', 'street', 'city', 'vat', mode='before')
    @classmethod
    def handle_false_strings(cls, v):
        """Convert False to None for string fields."""
        return None if v is False else v
    
    @field_validator('country_id', mode='before')
    @classmethod
    def handle_false_country(cls, v):
        """Convert False to None for country_id field."""
        return None if v is False else v


# Account models
class Account(OdooModel):
    """Represents an account in the chart of accounts."""
    code: str = Field(..., description="Account code")
    name: str = Field(..., description="Account name")
    account_type: str = Field(..., description="Account type")
    internal_group: Optional[str] = Field(None, description="Internal group")
    reconcile: bool = Field(default=False, description="Allow reconciliation")
    # Note: company_id field doesn't exist on account.account in Odoo 18


class AccountBalance(BaseModel):
    """Account balance information."""
    account_code: str = Field(..., description="Account code")
    account_name: str = Field(..., description="Account name")
    debit: float = Field(..., description="Total debit")
    credit: float = Field(..., description="Total credit")
    balance: float = Field(..., description="Balance (debit - credit)")
    date_from: Optional[str] = Field(None, description="Start date")
    date_to: Optional[str] = Field(None, description="End date")


# Journal models
class Journal(OdooModel):
    """Represents an accounting journal."""
    name: str = Field(..., description="Journal name")
    code: str = Field(..., description="Journal code")
    type: str = Field(..., description="Journal type")
    default_account_id: Optional[List[Any]] = Field(None, description="Default account")
    company_id: Optional[List[Any]] = Field(None, description="Company")
    currency_id: Optional[List[Any]] = Field(None, description="Currency")
    active: bool = Field(default=True, description="Active")
    
    @field_validator('currency_id', 'default_account_id', 'company_id', mode='before')
    @classmethod
    def handle_false_relations(cls, v):
        """Convert False to None for relation fields."""
        return None if v is False else v


class JournalEntry(OdooModel):
    """Represents a journal entry (account.move)."""
    name: str = Field(..., description="Entry number")
    date: str = Field(..., description="Entry date")  # Odoo returns dates as strings
    journal_id: Optional[List[Any]] = Field(None, description="Journal")
    state: str = Field(..., description="State (draft/posted)")
    move_type: str = Field(..., description="Move type")
    amount_total: float = Field(default=0.0, description="Total amount")
    amount_residual: float = Field(default=0.0, description="Amount due")
    partner_id: Optional[List[Any]] = Field(None, description="Partner")
    ref: Optional[str] = Field(None, description="Reference")
    narration: Optional[str] = Field(None, description="Internal note")
    currency_id: Optional[List[Any]] = Field(None, description="Currency")
    company_id: Optional[List[Any]] = Field(None, description="Company")
    
    @field_validator('name', mode='before')
    @classmethod
    def handle_false_name(cls, v):
        """Convert False to empty string for name."""
        return '' if v is False else v
    
    @field_validator('partner_id', 'journal_id', 'currency_id', 'company_id', mode='before')
    @classmethod
    def handle_false_relations(cls, v):
        """Convert False to None for relation fields."""
        return None if v is False else v
    
    @field_validator('ref', 'narration', mode='before')
    @classmethod
    def handle_false_strings(cls, v):
        """Convert False to None for string fields."""
        return None if v is False else v


class JournalEntryLine(BaseModel):
    """Represents a journal entry line (account.move.line)."""
    id: int = Field(..., description="Line ID")
    name: str = Field(..., description="Label")
    account_id: List[Any] = Field(..., description="Account")
    debit: float = Field(default=0.0, description="Debit amount")
    credit: float = Field(default=0.0, description="Credit amount")
    balance: float = Field(default=0.0, description="Balance")
    partner_id: Optional[List[Any]] = Field(None, description="Partner")
    date: str = Field(..., description="Date")
    move_id: List[Any] = Field(..., description="Journal entry")
    tax_ids: Optional[List[int]] = Field(None, description="Taxes")
    
    @field_validator('name', mode='before')
    @classmethod
    def handle_false_name(cls, v):
        """Convert False to empty string for name."""
        return '' if v is False else v
    
    @field_validator('partner_id', mode='before')
    @classmethod
    def handle_false_partner(cls, v):
        """Convert False to None for partner_id."""
        return None if v is False else v


class JournalEntryDetailed(JournalEntry):
    """Detailed journal entry with lines."""
    line_ids: List[JournalEntryLine] = Field(default_factory=list, description="Entry lines")


# Invoice models
class Invoice(JournalEntry):
    """Represents a customer invoice or vendor bill."""
    invoice_date: Optional[str] = Field(None, description="Invoice date")
    invoice_date_due: Optional[str] = Field(None, description="Due date")
    invoice_origin: Optional[str] = Field(None, description="Source document")
    payment_state: Optional[str] = Field(None, description="Payment state")
    currency_id: List[Any] = Field(..., description="Currency")
    ref: Optional[str] = Field(None, description="Reference")
    
    @field_validator('invoice_origin', 'ref', mode='before')
    @classmethod
    def handle_false_values(cls, v):
        """Convert False to None for string fields."""
        return None if v is False else v
    
    @property
    def is_invoice(self) -> bool:
        """Check if this is a customer invoice."""
        return self.move_type in ['out_invoice', 'out_refund']
    
    @property
    def is_bill(self) -> bool:
        """Check if this is a vendor bill."""
        return self.move_type in ['in_invoice', 'in_refund']


class InvoiceLine(BaseModel):
    """Represents an invoice line."""
    id: int = Field(..., description="Line ID")
    name: str = Field(..., description="Description")
    product_id: Optional[List[Any]] = Field(None, description="Product")
    account_id: List[Any] = Field(..., description="Account")
    quantity: float = Field(default=1.0, description="Quantity")
    price_unit: float = Field(default=0.0, description="Unit price")
    discount: float = Field(default=0.0, description="Discount %")
    price_subtotal: float = Field(default=0.0, description="Subtotal")
    price_total: float = Field(default=0.0, description="Total")
    
    @field_validator('product_id', mode='before')
    @classmethod
    def handle_false_product(cls, v):
        """Convert False to None for product_id."""
        return None if v is False else v


class InvoiceDetailed(Invoice):
    """Detailed invoice with lines."""
    invoice_line_ids: List[InvoiceLine] = Field(default_factory=list, description="Invoice lines")


# Payment models
class Payment(OdooModel):
    """Represents a payment."""
    name: str = Field(..., description="Payment name")
    date: str = Field(..., description="Date")  # Maps to payment_date in tool
    payment_date: str = Field(..., description="Payment date")
    amount: float = Field(..., description="Payment amount")
    payment_type: str = Field(..., description="Payment type (inbound/outbound)")
    partner_type: str = Field(..., description="Partner type (customer/supplier)")
    partner_id: Optional[List[Any]] = Field(None, description="Partner")
    journal_id: Optional[List[Any]] = Field(None, description="Payment journal")
    state: str = Field(..., description="State")
    currency_id: Optional[List[Any]] = Field(None, description="Currency")
    payment_method_id: Optional[List[Any]] = Field(None, description="Payment method")
    payment_method_line_id: Optional[List[Any]] = Field(None, description="Payment method line")
    ref: Optional[str] = Field(None, description="Reference")
    is_reconciled: bool = Field(default=False, description="Is reconciled")
    is_matched: bool = Field(default=False, description="Is matched")
    
    @field_validator('partner_id', 'journal_id', 'currency_id', 'payment_method_id', 'payment_method_line_id', mode='before')
    @classmethod
    def handle_false_relations(cls, v):
        """Convert False to None for relation fields."""
        return None if v is False else v
    
    @field_validator('ref', mode='before')
    @classmethod
    def handle_false_ref(cls, v):
        """Convert False to None for ref field."""
        return None if v is False else v


# Report models
class TrialBalanceLine(BaseModel):
    """Line in a trial balance report."""
    account_code: str = Field(..., description="Account code")
    account_name: str = Field(..., description="Account name")
    initial_debit: float = Field(default=0.0, description="Initial debit")
    initial_credit: float = Field(default=0.0, description="Initial credit")
    initial_balance: float = Field(default=0.0, description="Initial balance")
    period_debit: float = Field(default=0.0, description="Period debit")
    period_credit: float = Field(default=0.0, description="Period credit")
    ending_debit: float = Field(default=0.0, description="Ending debit")
    ending_credit: float = Field(default=0.0, description="Ending credit")
    ending_balance: float = Field(default=0.0, description="Ending balance")


class ProfitAndLossReport(BaseModel):
    """Profit and Loss report structure."""
    date_from: str = Field(..., description="Start date")
    date_to: str = Field(..., description="End date")
    revenue: Dict[str, float] = Field(default_factory=dict, description="Revenue accounts")
    expenses: Dict[str, float] = Field(default_factory=dict, description="Expense accounts")
    total_revenue: float = Field(default=0.0, description="Total revenue")
    total_expenses: float = Field(default=0.0, description="Total expenses")
    net_profit: float = Field(default=0.0, description="Net profit/loss")