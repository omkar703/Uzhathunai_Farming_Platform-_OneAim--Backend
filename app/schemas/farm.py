"""
Farm schemas for Uzhathunai v2.0.

Schemas for farm CRUD operations with GIS support.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, validator


class GeoJSONPoint(BaseModel):
    """Schema for GeoJSON Point geometry."""
    type: str = Field(..., pattern="^Point$")
    coordinates: List[float] = Field(..., min_items=2, max_items=2, description="[longitude, latitude]")
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate longitude and latitude ranges."""
        if len(v) != 2:
            raise ValueError('Coordinates must have exactly 2 values [longitude, latitude]')
        lon, lat = v
        if not (-180 <= lon <= 180):
            raise ValueError(f'Longitude must be between -180 and 180, got {lon}')
        if not (-90 <= lat <= 90):
            raise ValueError(f'Latitude must be between -90 and 90, got {lat}')
        return v


class GeoJSONPolygon(BaseModel):
    """Schema for GeoJSON Polygon geometry."""
    type: str = Field(..., pattern="^Polygon$")
    coordinates: List[List[List[float]]] = Field(..., description="Array of linear rings")
    
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


class FarmAttributes(BaseModel):
    """Schema for farm attributes structure."""
    soil_ec: Optional[float] = Field(None, description="Soil electrical conductivity")
    soil_ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH level")
    water_ec: Optional[float] = Field(None, description="Water electrical conductivity")
    water_ph: Optional[float] = Field(None, ge=0, le=14, description="Water pH level")
    
    class Config:
        extra = "allow"  # Allow additional fields


class FarmCreate(BaseModel):
    """Schema for creating farm."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=20)
    location: GeoJSONPoint = Field(..., description="Farm location as GeoJSON Point")
    boundary: Optional[GeoJSONPolygon] = Field(None, description="Farm boundary as GeoJSON Polygon")
    area: Optional[Decimal] = Field(None, ge=0)
    area_unit_id: Optional[UUID] = None
    farm_attributes: Optional[Dict[str, Any]] = Field(None, description="Farm attributes (soil EC, pH, water EC, pH, etc.)")
    manager_id: Optional[UUID] = None
    water_source_ids: Optional[List[UUID]] = Field(None, description="List of water source reference IDs")
    soil_type_ids: Optional[List[UUID]] = Field(None, description="List of soil type reference IDs")
    irrigation_mode_ids: Optional[List[UUID]] = Field(None, description="List of irrigation mode reference IDs")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class FarmUpdate(BaseModel):
    """Schema for updating farm."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=20)
    location: Optional[GeoJSONPoint] = Field(None, description="Farm location as GeoJSON Point")
    boundary: Optional[GeoJSONPolygon] = Field(None, description="Farm boundary as GeoJSON Polygon")
    area: Optional[Decimal] = Field(None, ge=0)
    area_unit_id: Optional[UUID] = None
    farm_attributes: Optional[Dict[str, Any]] = Field(None, description="Farm attributes to update")
    manager_id: Optional[UUID] = None
    water_source_ids: Optional[List[UUID]] = Field(None, description="List of water source reference IDs to replace existing")
    soil_type_ids: Optional[List[UUID]] = Field(None, description="List of soil type reference IDs to replace existing")
    irrigation_mode_ids: Optional[List[UUID]] = Field(None, description="List of irrigation mode reference IDs to replace existing")
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v


class FarmSupervisorResponse(BaseModel):
    """Schema for farm supervisor response."""
    id: str
    farm_id: str
    supervisor_id: str
    assigned_at: datetime
    assigned_by: Optional[str]
    
    @validator('id', 'farm_id', 'supervisor_id', 'assigned_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class FarmWaterSourceAdd(BaseModel):
    """Schema for adding water source to farm."""
    water_source_id: UUID = Field(..., description="Water source reference ID")


class FarmSoilTypeAdd(BaseModel):
    """Schema for adding soil type to farm."""
    soil_type_id: UUID = Field(..., description="Soil type reference ID")


class FarmIrrigationModeAdd(BaseModel):
    """Schema for adding irrigation mode to farm."""
    irrigation_mode_id: UUID = Field(..., description="Irrigation mode reference ID")


class ReferenceDataNested(BaseModel):
    """Nested reference data for responses."""
    id: str
    code: str
    display_name: Optional[str]
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


from pydantic import BaseModel, Field, validator, model_validator

class FarmWaterSourceResponse(BaseModel):
    """Schema for farm water source response."""
    id: str
    farm_id: str
    water_source_id: str
    created_at: datetime
    reference_data: ReferenceDataNested
    name: Optional[str] = None
    
    @validator('id', 'farm_id', 'water_source_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    @validator('reference_data', pre=True)
    def get_reference_data(cls, v, values):
        """Get reference data from water_source relationship."""
        # If it's already a dict/object that matches ReferenceDataNested
        if isinstance(v, dict):
            return v
        if hasattr(v, '__dict__'):
            return v # Let Pydantic from_attributes handle it
        return v
    
    @model_validator(mode='after')
    def populate_name(self):
        """Populate name from reference_data if available."""
        if not self.name and self.reference_data:
            self.name = self.reference_data.display_name or self.reference_data.code
        return self

    class Config:
        from_attributes = True


class FarmSoilTypeResponse(BaseModel):
    """Schema for farm soil type response."""
    id: str
    farm_id: str
    soil_type_id: str
    created_at: datetime
    reference_data: ReferenceDataNested
    name: Optional[str] = None
    
    @validator('id', 'farm_id', 'soil_type_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    @validator('reference_data', pre=True)
    def get_reference_data(cls, v, values):
        """Get reference data from soil_type relationship."""
        if isinstance(v, dict):
            return v
        if hasattr(v, '__dict__'):
            return v # Let Pydantic from_attributes handle it
        return v

    @model_validator(mode='after')
    def populate_name(self):
        """Populate name from reference_data if available."""
        if not self.name and self.reference_data:
            self.name = self.reference_data.display_name or self.reference_data.code
        return self
    
    class Config:
        from_attributes = True


class FarmIrrigationModeResponse(BaseModel):
    """Schema for farm irrigation mode response."""
    id: str
    farm_id: str
    irrigation_mode_id: str
    created_at: datetime
    reference_data: ReferenceDataNested
    name: Optional[str] = None
    
    @validator('id', 'farm_id', 'irrigation_mode_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    @validator('reference_data', pre=True)
    def get_reference_data(cls, v, values):
        """Get reference data from irrigation_mode relationship."""
        if isinstance(v, dict):
            return v
        if hasattr(v, '__dict__'):
            return v # Let Pydantic from_attributes handle it
        return v

    @model_validator(mode='after')
    def populate_name(self):
        """Populate name from reference_data if available."""
        if not self.name and self.reference_data:
            self.name = self.reference_data.display_name or self.reference_data.code
        return self

    class Config:
        from_attributes = True


class FarmResponse(BaseModel):
    """Schema for farm response."""
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    address: Optional[str]
    city: Optional[str]
    district: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    location: Optional[Dict[str, Any]] = Field(None, description="Farm location as GeoJSON Point")
    location_details: Optional[Dict[str, Any]] = Field(None, description="Location details with lat/lon")
    boundary: Optional[Dict[str, Any]] = Field(None, description="Farm boundary as GeoJSON Polygon")
    area: Optional[Decimal]
    area_unit_id: Optional[str]
    farm_attributes: Optional[Dict[str, Any]] = Field(None, description="Farm attributes (soil EC, pH, water EC, pH, etc.)")
    manager_id: Optional[str]
    water_source_ids: List[str] = Field(default_factory=list, description="List of water source reference IDs")
    soil_type_ids: List[str] = Field(default_factory=list, description="List of soil type reference IDs")
    irrigation_mode_ids: List[str] = Field(default_factory=list, description="List of irrigation mode reference IDs")
    water_sources: List[FarmWaterSourceResponse] = Field(default_factory=list, description="Water sources with reference data")
    soil_types: List[FarmSoilTypeResponse] = Field(default_factory=list, description="Soil types with reference data")
    irrigation_modes: List[FarmIrrigationModeResponse] = Field(default_factory=list, description="Irrigation modes with reference data")
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    
    @validator('id', 'organization_id', 'area_unit_id', 'manager_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
