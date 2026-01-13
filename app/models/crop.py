"""
Crop models for Uzhathunai v2.0.

Includes crop lifecycle tracking, yields, and photos.
Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, Text, Numeric, Date, Index, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import CropLifecycle


class Crop(Base):
    """
    Crops with lifecycle tracking from PLANNED to CLOSED.
    Matches DDL lines for crops table.
    """
    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id = Column(UUID(as_uuid=True), ForeignKey('plots.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    crop_type_id = Column(UUID(as_uuid=True), ForeignKey('crop_types.id'))
    crop_variety_id = Column(UUID(as_uuid=True), ForeignKey('crop_varieties.id'))
    area = Column(Numeric(15, 4))
    area_unit_id = Column(UUID(as_uuid=True), ForeignKey('measurement_units.id'))
    plant_count = Column(Integer)
    lifecycle = Column(SQLEnum(CropLifecycle, name='crop_lifecycle'), default=CropLifecycle.PLANNED)
    planned_date = Column(Date)
    planted_date = Column(Date)
    transplanted_date = Column(Date)
    production_start_date = Column(Date)
    completed_date = Column(Date)
    terminated_date = Column(Date)
    closed_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    plot = relationship("Plot", back_populates="crops")
    crop_type = relationship("CropType")
    crop_variety = relationship("CropVariety")
    area_unit = relationship("MeasurementUnit", foreign_keys=[area_unit_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    yields = relationship("CropYield", back_populates="crop", cascade="all, delete-orphan")
    photos = relationship("CropLifecyclePhoto", back_populates="crop", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_crops_plot', 'plot_id'),
        Index('idx_crops_lifecycle', 'lifecycle'),
        Index('idx_crops_type', 'crop_type_id'),
    )


class CropLifecyclePhoto(Base):
    """
    Photos for crop lifecycle documentation.
    Can be associated with yields through crop_yield_photos.
    Matches DDL lines for crop_lifecycle_photos table.
    """
    __tablename__ = "crop_lifecycle_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_key = Column(String(500))
    caption = Column(Text)
    photo_date = Column(Date)
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    crop = relationship("Crop", back_populates="photos")
    uploader = relationship("User")
    yield_associations = relationship("CropYieldPhoto", back_populates="photo", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_crop_lifecycle_photos_crop', 'crop_id'),
        Index('idx_crop_lifecycle_photos_date', 'photo_date'),
    )


class CropYield(Base):
    """
    Crop yield records (PLANNED and ACTUAL).
    Supports both area-based and count-based yields.
    Matches DDL lines for crop_yields table.
    """
    __tablename__ = "crop_yields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), nullable=False)
    yield_type = Column(String(20), nullable=False)  # PLANNED, ACTUAL
    harvest_date = Column(Date)
    quantity = Column(Numeric(15, 4), nullable=False)
    quantity_unit_id = Column(UUID(as_uuid=True), ForeignKey('measurement_units.id'))
    harvest_area = Column(Numeric(15, 4))  # Optional for area-based yields
    harvest_area_unit_id = Column(UUID(as_uuid=True), ForeignKey('measurement_units.id'))
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    crop = relationship("Crop", back_populates="yields")
    quantity_unit = relationship("MeasurementUnit", foreign_keys=[quantity_unit_id])
    harvest_area_unit = relationship("MeasurementUnit", foreign_keys=[harvest_area_unit_id])
    creator = relationship("User")
    photos = relationship("CropYieldPhoto", back_populates="crop_yield", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(harvest_area IS NULL AND harvest_area_unit_id IS NULL) OR "
            "(harvest_area IS NOT NULL AND harvest_area_unit_id IS NOT NULL)",
            name="chk_harvest_area_unit"
        ),
        Index('idx_crop_yields_crop', 'crop_id'),
    )


class CropYieldPhoto(Base):
    """
    Many-to-many relationship between crop yields and photos.
    Matches DDL lines for crop_yield_photos table.
    """
    __tablename__ = "crop_yield_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_yield_id = Column(UUID(as_uuid=True), ForeignKey('crop_yields.id', ondelete='CASCADE'), nullable=False)
    photo_id = Column(UUID(as_uuid=True), ForeignKey('crop_lifecycle_photos.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    crop_yield = relationship("CropYield", back_populates="photos")
    photo = relationship("CropLifecyclePhoto", back_populates="yield_associations")

    # Indexes
    __table_args__ = (
        Index('idx_crop_yield_photos_yield', 'crop_yield_id'),
        Index('idx_crop_yield_photos_photo', 'photo_id'),
    )
