"""
Farm models for Uzhathunai v2.0.

Includes PostGIS geography columns for location and boundary.
Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography
import uuid

from app.core.database import Base


class Farm(Base):
    """
    Farms with geographic boundaries and attributes.
    Uses PostGIS for location (POINT) and boundary (POLYGON).
    Matches DDL lines for farms table.
    """
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    address = Column(Text)
    district = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    location = Column(Geography(geometry_type='POINT', srid=4326, spatial_index=False))
    boundary = Column(Geography(geometry_type='POLYGON', srid=4326, spatial_index=False))
    area = Column(Numeric(15, 4))
    area_unit_id = Column(UUID(as_uuid=True), ForeignKey('measurement_units.id'))
    farm_attributes = Column(JSONB)  # {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0}
    manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
    manager = relationship("User", foreign_keys=[manager_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    area_unit = relationship("MeasurementUnit", foreign_keys=[area_unit_id])
    supervisors = relationship("FarmSupervisor", back_populates="farm", cascade="all, delete-orphan")
    water_sources = relationship("FarmWaterSource", back_populates="farm", cascade="all, delete-orphan")
    soil_types = relationship("FarmSoilType", back_populates="farm", cascade="all, delete-orphan")
    irrigation_modes = relationship("FarmIrrigationMode", back_populates="farm", cascade="all, delete-orphan")
    plots = relationship("Plot", back_populates="farm", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_farms_org', 'organization_id'),
        Index('idx_farms_location', 'location', postgresql_using='gist'),
        Index('idx_farms_boundary', 'boundary', postgresql_using='gist'),
        Index('idx_farms_manager', 'manager_id'),
        Index('idx_farms_attributes', 'farm_attributes', postgresql_using='gin'),
    )


class FarmSupervisor(Base):
    """
    Many-to-many relationship between farms and supervisors.
    Matches DDL lines for farm_supervisors table.
    """
    __tablename__ = "farm_supervisors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.id', ondelete='CASCADE'), nullable=False)
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    assigned_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="supervisors")
    supervisor = relationship("User", foreign_keys=[supervisor_id])
    assigner = relationship("User", foreign_keys=[assigned_by])


class FarmWaterSource(Base):
    """
    Many-to-many relationship between farms and water sources.
    Matches DDL lines for farm_water_sources table.
    """
    __tablename__ = "farm_water_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.id', ondelete='CASCADE'), nullable=False)
    water_source_id = Column(UUID(as_uuid=True), ForeignKey('reference_data.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="water_sources")
    water_source = relationship("ReferenceData")


class FarmSoilType(Base):
    """
    Many-to-many relationship between farms and soil types.
    Matches DDL lines for farm_soil_types table.
    """
    __tablename__ = "farm_soil_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.id', ondelete='CASCADE'), nullable=False)
    soil_type_id = Column(UUID(as_uuid=True), ForeignKey('reference_data.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="soil_types")
    soil_type = relationship("ReferenceData")


class FarmIrrigationMode(Base):
    """
    Many-to-many relationship between farms and irrigation modes.
    Matches DDL lines for farm_irrigation_modes table.
    """
    __tablename__ = "farm_irrigation_modes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.id', ondelete='CASCADE'), nullable=False)
    irrigation_mode_id = Column(UUID(as_uuid=True), ForeignKey('reference_data.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="irrigation_modes")
    irrigation_mode = relationship("ReferenceData")
