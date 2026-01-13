"""
Finance Category models for Uzhathunai v2.0.

Supports both system-defined and organization-specific finance categories.
Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, Text, CheckConstraint, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import TransactionType


class FinanceCategory(Base):
    """
    Finance transaction categories (INCOME and EXPENSE).
    Supports both system-defined and organization-specific categories.
    Matches DDL lines for finance_categories table.
    """
    __tablename__ = "finance_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(SQLEnum(TransactionType, name='transaction_type'), nullable=False)
    code = Column(String(50), nullable=False)
    is_system_defined = Column(Boolean, default=True)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    owner_organization = relationship("Organization", foreign_keys=[owner_org_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    translations = relationship("FinanceCategoryTranslation", back_populates="category", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(is_system_defined = true AND owner_org_id IS NULL) OR "
            "(is_system_defined = false AND owner_org_id IS NOT NULL)",
            name="chk_finance_category_ownership"
        ),
        UniqueConstraint("transaction_type", "code", "is_system_defined", "owner_org_id"),
    )


class FinanceCategoryTranslation(Base):
    """
    Multilingual translations for finance categories.
    Matches DDL lines for finance_category_translations table.
    """
    __tablename__ = "finance_category_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('finance_categories.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    category = relationship("FinanceCategory", back_populates="translations")
