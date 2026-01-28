"""
Input Item models (categories and items) for Uzhathunai v2.0.

Supports both system-defined and organization-specific input items.
Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, Text, CheckConstraint, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import InputItemType


class InputItemCategory(Base):
    """
    Input item categories (e.g., Fertilizers, Pesticides, Herbicides).
    Supports both system-defined and organization-specific categories.
    Matches DDL lines for input_item_categories table.
    """
    __tablename__ = "input_item_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    translations = relationship("InputItemCategoryTranslation", back_populates="category", cascade="all, delete-orphan")
    items = relationship("InputItem", back_populates="category", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(is_system_defined = true AND owner_org_id IS NULL) OR "
            "(is_system_defined = false AND owner_org_id IS NOT NULL)",
            name="chk_input_category_ownership"
        ),
        UniqueConstraint("code", "is_system_defined", "owner_org_id"),
    )


class InputItemCategoryTranslation(Base):
    """
    Multilingual translations for input item categories.
    Matches DDL lines for input_item_category_translations table.
    """
    __tablename__ = "input_item_category_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('input_item_categories.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    category = relationship("InputItemCategory", back_populates="translations")


class InputItem(Base):
    """
    Input items (e.g., Urea, NPK 19-19-19, Glyphosate).
    Supports both system-defined and organization-specific items.
    Includes item_metadata JSONB for brand, composition, NPK ratio, etc.
    Matches DDL lines for input_items table.
    """
    __tablename__ = "input_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('input_item_categories.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(50), nullable=False)
    is_system_defined = Column(Boolean, default=True)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    type = Column(SQLEnum(InputItemType, name='input_item_type'), nullable=True) # made nullable for backward compat, but logic should enforce it
    default_unit_id = Column(UUID(as_uuid=True), ForeignKey('measurement_units.id'), nullable=True)
    item_metadata = Column(JSONB)  # {"brand": "Tata", "composition": "Urea 46% N", "npk_ratio": "46-0-0", ...}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    category = relationship("InputItemCategory", back_populates="items")
    owner_organization = relationship("Organization", foreign_keys=[owner_org_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    translations = relationship("InputItemTranslation", back_populates="input_item", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(is_system_defined = true AND owner_org_id IS NULL) OR "
            "(is_system_defined = false AND owner_org_id IS NOT NULL)",
            name="chk_input_item_ownership"
        ),
        UniqueConstraint("category_id", "code", "is_system_defined", "owner_org_id"),
    )


class InputItemTranslation(Base):
    """
    Multilingual translations for input items.
    Matches DDL lines for input_item_translations table.
    """
    __tablename__ = "input_item_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_item_id = Column(UUID(as_uuid=True), ForeignKey('input_items.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    input_item = relationship("InputItem", back_populates="translations")
