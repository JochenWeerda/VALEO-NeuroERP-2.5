"""
SQLAlchemy models for VALEO-NeuroERP
Database entities following domain-driven design
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ...core.database import Base


# Shared Models
class Tenant(Base):
    """Tenant model for multi-tenancy"""
    __tablename__ = "shared_tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=False)
    settings = Column(Text, default="{}")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    """User model"""
    __tablename__ = "shared_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    keycloak_id = Column(String, nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    roles = Column(Text, default="[]")  # JSON array of roles
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


# CRM Models
class Customer(Base):
    """Customer model"""
    __tablename__ = "crm_customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_number = Column(String(50), nullable=False)
    company_name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    country = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)
    website = Column(String(100), nullable=True)
    credit_limit = Column(DECIMAL(15, 2), nullable=True)
    payment_terms = Column(String(50), nullable=True)
    tax_id = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Lead(Base):
    """Lead model"""
    __tablename__ = "crm_leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    priority = Column(String(10), default="medium")
    estimated_value = Column(DECIMAL(15, 2), nullable=True)
    company_name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    assigned_to = Column(String, ForeignKey("shared_users.id"), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    converted_to_customer_id = Column(String, ForeignKey("crm_customers.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Contact(Base):
    """Contact model"""
    __tablename__ = "crm_contacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    position = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    customer_id = Column(String, ForeignKey("crm_customers.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


# Inventory Models
class Article(Base):
    """Article/Product model"""
    __tablename__ = "inventory_articles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_number = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    barcode = Column(String(50), nullable=True)
    supplier_number = Column(String(50), nullable=True)
    purchase_price = Column(DECIMAL(10, 2), nullable=True)
    sales_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    min_stock = Column(DECIMAL(10, 2), nullable=True)
    max_stock = Column(DECIMAL(10, 2), nullable=True)
    weight = Column(DECIMAL(8, 2), nullable=True)
    dimensions = Column(String(50), nullable=True)
    current_stock = Column(DECIMAL(10, 2), default=0)
    reserved_stock = Column(DECIMAL(10, 2), default=0)
    available_stock = Column(DECIMAL(10, 2), default=0)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Warehouse(Base):
    """Warehouse model"""
    __tablename__ = "inventory_warehouses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    warehouse_code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    country = Column(String(2), default="DE")
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    warehouse_type = Column(String(20), default="standard")
    total_capacity = Column(DECIMAL(12, 2), nullable=True)
    used_capacity = Column(DECIMAL(12, 2), default=0)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class StockMovement(Base):
    """Stock movement model"""
    __tablename__ = "inventory_stock_movements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("inventory_articles.id"), nullable=False)
    warehouse_id = Column(String, ForeignKey("inventory_warehouses.id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # in, out, transfer, adjustment
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_cost = Column(DECIMAL(10, 2), nullable=True)
    reference_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    previous_stock = Column(DECIMAL(10, 2), nullable=False)
    new_stock = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(12, 2), nullable=True)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InventoryCount(Base):
    """Inventory count model"""
    __tablename__ = "inventory_counts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    warehouse_id = Column(String, ForeignKey("inventory_warehouses.id"), nullable=False)
    count_date = Column(DateTime(timezone=True), server_default=func.now())
    counted_by = Column(String, ForeignKey("shared_users.id"), nullable=False)
    status = Column(String(20), default="draft")  # draft, completed, approved
    total_items = Column(Integer, default=0)
    discrepancies_found = Column(Integer, default=0)
    approved_by = Column(String, ForeignKey("shared_users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Finance Models
class Account(Base):
    """Chart of accounts model"""
    __tablename__ = "finance_accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_number = Column(String(20), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False)  # asset, liability, equity, revenue, expense
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_summary = Column(Boolean, default=False)
    balance = Column(DECIMAL(15, 2), default=0)
    last_transaction_date = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class JournalEntry(Base):
    """Journal entry model"""
    __tablename__ = "finance_journal_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entry_number = Column(String(20), nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False)
    posting_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(200), nullable=False)
    reference = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False)
    status = Column(String(20), default="draft")  # draft, posted, reversed
    total_debit = Column(DECIMAL(15, 2), default=0)
    total_credit = Column(DECIMAL(15, 2), default=0)
    posted_by = Column(String, ForeignKey("shared_users.id"), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    reversed_entry_id = Column(String, ForeignKey("finance_journal_entries.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("shared_tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JournalEntryLine(Base):
    """Journal entry line model"""
    __tablename__ = "finance_journal_entry_lines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    journal_entry_id = Column(String, ForeignKey("finance_journal_entries.id"), nullable=False)
    account_id = Column(String, ForeignKey("finance_accounts.id"), nullable=False)
    debit = Column(DECIMAL(15, 2), default=0)
    credit = Column(DECIMAL(15, 2), default=0)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())