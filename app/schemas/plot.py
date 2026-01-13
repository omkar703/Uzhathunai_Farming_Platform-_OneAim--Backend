"""
Plot schemas for Uzhathunai v2.0.

Schemas for plot CRUD operations with GIS support.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, validator


class GeoJSONPolygon(BaseModel):
    """Schema for GeoJSON Polygon geometry."""
    type: str = Field(..., pattern="^Polygon$")
    coordinates: list[list[list[float]]] = Field(..., description="Array of linear rings")
    
    @validator('coordinates')
    def validate_polygon(cls, v):
        """Validate polygon structure."""
        if not v or len(v) == 0:
            raise ValueError('Polygon must have at least one ring')
        
        # Validate outer ring
        outer_ring = v[0]
        if len(outer_ring) < 4:
            raise ValueError('Polygon ring must have at least 4 points')
        
        # Validate closed ring
        if outer_ring[0] != outer_ring[-1]:
            raise ValueError('Polygon ring must be closed (first point equals last point)')
        
        # Validate coordinate ranges
        for ring in v:
            for point in ring:
                if len(point) != 2:
                    raise ValueError('Each point must have exactly 2 coordinates [longitude, latitude]')
                lon, lat = point
                if not (-180 <= lon <= 180):
                    raise ValueError(f'Longitude must be between -180 and 180, got {lon}')
                if not (-90 <= lat <= 90):
                    raise ValueError(f'Latitude must be between -90 and 90, got {lat}')
        
        return v


class PlotAttributes(BaseModel):
    """Schema for plot attributes structure."""
    soil_ec: Optional[float] = Field(None, description="Soil electrical conductivity")
    soil_ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH level")
    water_ec: Optional[float] = Field(None, description="Water electrical conductivity")
    water_ph: Optional[float] = Field(None, ge=0, le=14, description="Water pH level")
    
    class Config:
        extra = "allow"  # Allow additional fields


class PlotCreate(BaseModel):
    """Schema for creating plot."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    boundary: Optional[GeoJSONPolygon] = Field(None, description="Plot boundary as GeoJSON Polygon")
    area: Optional[Decimal] = Field(None, ge=0)
    area_unit_id: Optional[UUID] = None
    plot_attributes: Optional[Dict[str, Any]] = Field(None, description="Plot attributes (soil EC, pH, water EC, pH, etc.)")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class PlotUpdate(BaseModel):
    """Schema for updating plot."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    boundary: Optional[GeoJSONPolygon] = Field(None, description="Plot boundary as GeoJSON Polygon")
    area: Optional[Decimal] = Field(None, ge=0)
    area_unit_id: Optional[UUID] = None
    plot_attributes: Optional[Dict[str, Any]] = Field(None, description="Plot attributes to update")
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v


class PlotWaterSourceAdd(BaseModel):
    """Schema for adding water source to plot."""
    water_source_id: UUID = Field(..., description="Water source reference ID")


class PlotSoilTypeAdd(BaseModel):
    """Schema for adding soil type to plot."""
    soil_type_id: UUID = Field(..., description="Soil type reference ID")


class PlotIrrigationModeAdd(BaseModel):
    """Schema for adding irrigation mode to plot."""
    irrigation_mode_id: UUID = Field(..., description="Irrigation mode reference ID")


class PlotResponse(BaseModel):
    """Schema for plot response."""
    id: str
    farm_id: str
    name: str
    description: Optional[str]
    boundary: Optional[Dict[str, Any]] = Field(None, description="Plot boundary as GeoJSON Polygon")
    area: Optional[Decimal]
    area_unit_id: Optional[str]
    plot_attributes: Optional[Dict[str, Any]] = Field(None, description="Plot attributes (soil EC, pH, water EC, pH, etc.)")
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    
    @validator('id', 'farm_id', 'area_unit_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
