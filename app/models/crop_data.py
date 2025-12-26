"""
Crop hierarchy models (categories, types, varieties) for Uzhathunai v2.0.

Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class CropCategory(Base):
    """
    Crop categories (e.g., Vegetables, Fruits, Cereals).
    Matches DDL lines for crop_categories table.
    """
    __tablename__ = "crop_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    translations = relationship("CropCategoryTranslation", back_populates="crop_category", cascade="all, delete-orphan")
    crop_types = relationship("CropType", back_populates="category", cascade="all, delete-orphan")


class CropCategoryTranslation(Base):
    """
    Multilingual translations for crop categories.
    Matches DDL lines for crop_category_translations table.
    """
    __tablename__ = "crop_category_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_category_id = Column(UUID(as_uuid=True), ForeignKey('crop_categories.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Relationships
    crop_category = relationship("CropCategory", back_populates="translations")


class CropType(Base):
    """
    Crop types within categories (e.g., Tomato, Potato under Vegetables).
    Matches DDL lines for crop_types table.
    """
    __tablename__ = "crop_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('crop_categories.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("CropCategory", back_populates="crop_types")
    translations = relationship("CropTypeTranslation", back_populates="crop_type", cascade="all, delete-orphan")
    varieties = relationship("CropVariety", back_populates="crop_type", cascade="all, delete-orphan")


class CropTypeTranslation(Base):
    """
    Multilingual translations for crop types.
    Matches DDL lines for crop_type_translations table.
    """
    __tablename__ = "crop_type_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_type_id = Column(UUID(as_uuid=True), ForeignKey('crop_types.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Relationships
    crop_type = relationship("CropType", back_populates="translations")


class CropVariety(Base):
    """
    Crop varieties within types (e.g., Cherry Tomato, Beefsteak Tomato under Tomato).
    Includes variety_metadata JSONB for maturity days, yield potential, spacing, etc.
    Matches DDL lines for crop_varieties table.
    """
    __tablename__ = "crop_varieties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_type_id = Column(UUID(as_uuid=True), ForeignKey('crop_types.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    variety_metadata = Column(JSONB)  # {"maturity_days": 90, "yield_potential_kg_per_acre": 15000, ...}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    crop_type = relationship("CropType", back_populates="varieties")
    translations = relationship("CropVarietyTranslation", back_populates="crop_variety", cascade="all, delete-orphan")


class CropVarietyTranslation(Base):
    """
    Multilingual translations for crop varieties.
    Matches DDL lines for crop_variety_translations table.
    """
    __tablename__ = "crop_variety_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_variety_id = Column(UUID(as_uuid=True), ForeignKey('crop_varieties.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Relationships
    crop_variety = relationship("CropVariety", back_populates="translations")
