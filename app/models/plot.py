"""
Plot models for Uzhathunai v2.0.

Includes PostGIS geography columns for boundary.
Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography
import uuid

from app.core.database import Base


class Plot(Base):
    """
    Plots within farms with geographic boundaries and attributes.
    Uses PostGIS for boundary (POLYGON).
    Matches DDL lines for plots table.
    """
    __tablename__ = "plots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    boundary = Column(Geography(geometry_type='POLYGON', srid=4326, spatial_index=False))
    area = Column(Numeric(15, 4))
    area_unit_id = Column(UUID(as_uuid=True), ForeignKey('measurement_units.id'))
    plot_attributes = Column(JSONB)  # {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0}
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    farm = relationship("Farm", back_populates="plots")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    area_unit = relationship("MeasurementUnit", foreign_keys=[area_unit_id])
    water_sources = relationship("PlotWaterSource", back_populates="plot", cascade="all, delete-orphan")
    soil_types = relationship("PlotSoilType", back_populates="plot", cascade="all, delete-orphan")
    irrigation_modes = relationship("PlotIrrigationMode", back_populates="plot", cascade="all, delete-orphan")
    crops = relationship("Crop", back_populates="plot", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_plots_farm', 'farm_id'),
        Index('idx_plots_boundary', 'boundary', postgresql_using='gist'),
        Index('idx_plots_attributes', 'plot_attributes', postgresql_using='gin'),
    )


class PlotWaterSource(Base):
    """
    Many-to-many relationship between plots and water sources.
    Matches DDL lines for plot_water_sources table.
    """
    __tablename__ = "plot_water_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id = Column(UUID(as_uuid=True), ForeignKey('plots.id', ondelete='CASCADE'), nullable=False)
    water_source_id = Column(UUID(as_uuid=True), ForeignKey('reference_data.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    plot = relationship("Plot", back_populates="water_sources")
    water_source = relationship("ReferenceData")


class PlotSoilType(Base):
    """
    Many-to-many relationship between plots and soil types.
    Matches DDL lines for plot_soil_types table.
    """
    __tablename__ = "plot_soil_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id = Column(UUID(as_uuid=True), ForeignKey('plots.id', ondelete='CASCADE'), nullable=False)
    soil_type_id = Column(UUID(as_uuid=True), ForeignKey('reference_data.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    plot = relationship("Plot", back_populates="soil_types")
    soil_type = relationship("ReferenceData")


class PlotIrrigationMode(Base):
    """
    Many-to-many relationship between plots and irrigation modes.
    Matches DDL lines for plot_irrigation_modes table.
    """
    __tablename__ = "plot_irrigation_modes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id = Column(UUID(as_uuid=True), ForeignKey('plots.id', ondelete='CASCADE'), nullable=False)
    irrigation_mode_id = Column(UUID(as_uuid=True), ForeignKey('reference_data.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    plot = relationship("Plot", back_populates="irrigation_modes")
    irrigation_mode = relationship("ReferenceData")
