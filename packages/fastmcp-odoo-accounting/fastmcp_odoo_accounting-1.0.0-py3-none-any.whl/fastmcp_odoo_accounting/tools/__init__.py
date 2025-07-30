"""Odoo Accounting MCP Tools.

This module contains all the tool definitions for interacting with Odoo Accounting data.
"""

# Import all tools to register them with the server
from . import partners
from . import accounts
from . import invoices
from . import journals
from . import payments
from . import reports

__all__ = [
    "partners",
    "accounts", 
    "invoices",
    "journals",
    "payments",
    "reports"
]