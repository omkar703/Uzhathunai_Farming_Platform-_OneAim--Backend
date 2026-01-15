"""
Plot service for managing plots with GIS support and ownership validation.
"""
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
import json

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.models.plot import (
    Plot, PlotWaterSource, PlotSoilType, PlotIrrigationMode
)
from app.models.farm import Farm
from app.schemas.plot import PlotCreate, PlotUpdate, PlotResponse
from app.services.spatial_service import SpatialService

logger = get_logger(__name__)


class PlotService:
    """Service for plot operations with GIS support."""
    
    def __init__(self, db: Session):
        self.db = db
        self.spatial_service = SpatialService(db)
    
    def create_plot(
        self,
        farm_id: UUID,
        data: PlotCreate,
        org_id: UUID,
        user_id: UUID
    ) -> PlotResponse:
        """
        Create a new plot with GIS validation.
        
        Args:
            farm_id: Farm ID
            data: Plot creation data
            org_id: Organization ID
            user_id: User ID creating the plot
            
        Returns:
            Created plot
            
        Raises:
            NotFoundError: If farm not found
            ValidationError: If boundary is invalid or plot is outside farm
        """
        # Validate farm exists and belongs to org
        farm = self.db.query(Farm).filter(
            and_(
                Farm.id == farm_id,
                Farm.organization_id == org_id,
                Farm.is_active == True
            )
        ).first()
        
        if not farm:
            raise NotFoundError(
                message=f"Farm {farm_id} not found",
                error_code="FARM_NOT_FOUND",
                details={"farm_id": str(farm_id)}
            )
        
        # Validate boundary if provided
        boundary_wkt = None
        if data.boundary:
            self.spatial_service.validate_boundary(data.boundary.dict())
            
            # Validate plot is within farm boundary if farm has boundary
            if farm.boundary:
                # Use PostGIS to get GeoJSON directly instead of parsing WKT
                farm_boundary_geojson = self._get_boundary_as_geojson(farm.id)
                if farm_boundary_geojson:
                    self.spatial_service.validate_plot_within_farm(
                        data.boundary.dict(),
                        farm_boundary_geojson
                    )
            
            # Convert GeoJSON to WKT for PostGIS
            boundary_coords = data.boundary.coordinates[0]
            boundary_wkt = self.spatial_service.create_polygon(boundary_coords)
        
        # Calculate area if boundary provided and area not specified
        calculated_area = None
        if data.boundary and not data.area:
            calculated_area = self.spatial_service.calculate_area(data.boundary.dict())
        
        # Create plot
        plot = Plot(
            farm_id=farm_id,
            name=data.name,
            description=data.description,
            boundary=boundary_wkt,
            area=data.area or calculated_area,
            area_unit_id=data.area_unit_id,
            plot_attributes=data.plot_attributes or {},
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(plot)
        self.db.commit()
        self.db.refresh(plot)
        
        logger.info(
            "Created plot",
            extra={
                "plot_id": str(plot.id),
                "farm_id": str(farm_id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "name": data.name,
                "has_boundary": boundary_wkt is not None,
                "area": float(plot.area) if plot.area else None
            }
        )
        
        return self._to_response(plot)
    
    def get_plots_by_farm(
        self,
        farm_id: UUID,
        org_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[PlotResponse], int]:
        """
        Get plots for a farm with pagination.
        
        Args:
            farm_id: Farm ID
            org_id: Organization ID
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            
        Returns:
            Tuple of (list of plots, total count)
            
        Raises:
            NotFoundError: If farm not found
        """
        # Validate farm exists and belongs to org
        farm = self.db.query(Farm).filter(
            and_(
                Farm.id == farm_id,
                Farm.organization_id == org_id,
                Farm.is_active == True
            )
        ).first()
        
        if not farm:
            raise NotFoundError(
                message=f"Farm {farm_id} not found",
                error_code="FARM_NOT_FOUND",
                details={"farm_id": str(farm_id)}
            )
        
        offset = (page - 1) * limit
        
        # Query plots
        query = (
            self.db.query(Plot)
            .filter(
                and_(
                    Plot.farm_id == farm_id,
                    Plot.is_active == True
                )
            )
            .order_by(Plot.created_at.desc())
        )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        plots = query.offset(offset).limit(limit).all()
        
        logger.info(
            "Retrieved plots by farm",
            extra={
                "farm_id": str(farm_id),
                "org_id": str(org_id),
                "page": page,
                "limit": limit,
                "count": len(plots),
                "total": total
            }
        )
        
        return [self._to_response(plot) for plot in plots], total
    
    def get_plot_by_id(
        self,
        plot_id: UUID,
        org_id: UUID
    ) -> PlotResponse:
        """
        Get plot by ID with ownership validation.
        
        Args:
            plot_id: Plot ID
            org_id: Organization ID
            
        Returns:
            Plot details
            
        Raises:
            NotFoundError: If plot not found or farm not owned by organization
        """
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .options(
                joinedload(Plot.farm),
                joinedload(Plot.area_unit),
                joinedload(Plot.water_sources),
                joinedload(Plot.soil_types),
                joinedload(Plot.irrigation_modes)
            )
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        logger.info(
            "Retrieved plot by ID",
            extra={
                "plot_id": str(plot_id),
                "org_id": str(org_id)
            }
        )
        
        return self._to_response(plot)
    
    def update_plot(
        self,
        plot_id: UUID,
        data: PlotUpdate,
        org_id: UUID,
        user_id: UUID
    ) -> PlotResponse:
        """
        Update plot with GIS validation.
        
        Args:
            plot_id: Plot ID
            data: Plot update data
            org_id: Organization ID
            user_id: User ID updating the plot
            
        Returns:
            Updated plot
            
        Raises:
            NotFoundError: If plot not found
            ValidationError: If boundary is invalid or plot is outside farm
        """
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        # Get farm for boundary validation
        farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
        
        # Update basic fields
        if data.name is not None:
            plot.name = data.name
        if data.description is not None:
            plot.description = data.description
        if data.is_active is not None:
            plot.is_active = data.is_active
        
        # Update boundary if provided
        if data.boundary:
            self.spatial_service.validate_boundary(data.boundary.dict())
            
            # Validate plot is within farm boundary if farm has boundary
            if farm.boundary:
                # Use PostGIS to get GeoJSON directly instead of parsing WKT
                farm_boundary_geojson = self._get_boundary_as_geojson(farm.id)
                if farm_boundary_geojson:
                    self.spatial_service.validate_plot_within_farm(
                        data.boundary.dict(),
                        farm_boundary_geojson
                    )
            
            boundary_coords = data.boundary.coordinates[0]
            plot.boundary = self.spatial_service.create_polygon(boundary_coords)
            
            # Recalculate area if boundary changed and area not explicitly provided
            if data.area is None:
                calculated_area = self.spatial_service.calculate_area(data.boundary.dict())
                plot.area = calculated_area
        
        # Update area if provided
        if data.area is not None:
            plot.area = data.area
        if data.area_unit_id is not None:
            plot.area_unit_id = data.area_unit_id
        
        # Update plot attributes
        if data.plot_attributes is not None:
            plot.plot_attributes = data.plot_attributes
        
        plot.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(plot)
        
        logger.info(
            "Updated plot",
            extra={
                "plot_id": str(plot_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_response(plot)
    
    def delete_plot(
        self,
        plot_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) plot.
        
        Args:
            plot_id: Plot ID
            org_id: Organization ID
            user_id: User ID deleting the plot
            
        Raises:
            NotFoundError: If plot not found
        """
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        # Soft delete
        plot.is_active = False
        plot.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted plot",
            extra={
                "plot_id": str(plot_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def add_water_source(
        self,
        plot_id: UUID,
        water_source_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Add water source to plot.
        
        Args:
            plot_id: Plot ID
            water_source_id: Water source reference data ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If plot not found
            ValidationError: If water source already added
        """
        # Validate plot exists and belongs to org
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        # Check if water source already added
        existing = self.db.query(PlotWaterSource).filter(
            and_(
                PlotWaterSource.plot_id == plot_id,
                PlotWaterSource.water_source_id == water_source_id
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Water source {water_source_id} already added to plot {plot_id}",
                error_code="WATER_SOURCE_ALREADY_ADDED",
                details={
                    "plot_id": str(plot_id),
                    "water_source_id": str(water_source_id)
                }
            )
        
        # Add water source
        water_source = PlotWaterSource(
            plot_id=plot_id,
            water_source_id=water_source_id
        )
        
        self.db.add(water_source)
        self.db.commit()
        
        logger.info(
            "Added water source to plot",
            extra={
                "plot_id": str(plot_id),
                "water_source_id": str(water_source_id),
                "org_id": str(org_id)
            }
        )
    
    def add_soil_type(
        self,
        plot_id: UUID,
        soil_type_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Add soil type to plot.
        
        Args:
            plot_id: Plot ID
            soil_type_id: Soil type reference data ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If plot not found
            ValidationError: If soil type already added
        """
        # Validate plot exists and belongs to org
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        # Check if soil type already added
        existing = self.db.query(PlotSoilType).filter(
            and_(
                PlotSoilType.plot_id == plot_id,
                PlotSoilType.soil_type_id == soil_type_id
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Soil type {soil_type_id} already added to plot {plot_id}",
                error_code="SOIL_TYPE_ALREADY_ADDED",
                details={
                    "plot_id": str(plot_id),
                    "soil_type_id": str(soil_type_id)
                }
            )
        
        # Add soil type
        soil_type = PlotSoilType(
            plot_id=plot_id,
            soil_type_id=soil_type_id
        )
        
        self.db.add(soil_type)
        self.db.commit()
        
        logger.info(
            "Added soil type to plot",
            extra={
                "plot_id": str(plot_id),
                "soil_type_id": str(soil_type_id),
                "org_id": str(org_id)
            }
        )
    
    def add_irrigation_mode(
        self,
        plot_id: UUID,
        irrigation_mode_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Add irrigation mode to plot.
        
        Args:
            plot_id: Plot ID
            irrigation_mode_id: Irrigation mode reference data ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If plot not found
            ValidationError: If irrigation mode already added
        """
        # Validate plot exists and belongs to org
        plot = (
            self.db.query(Plot)
            .join(Farm)
            .filter(
                and_(
                    Plot.id == plot_id,
                    Farm.organization_id == org_id,
                    Plot.is_active == True,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not plot:
            raise NotFoundError(
                message=f"Plot {plot_id} not found",
                error_code="PLOT_NOT_FOUND",
                details={"plot_id": str(plot_id)}
            )
        
        # Check if irrigation mode already added
        existing = self.db.query(PlotIrrigationMode).filter(
            and_(
                PlotIrrigationMode.plot_id == plot_id,
                PlotIrrigationMode.irrigation_mode_id == irrigation_mode_id
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Irrigation mode {irrigation_mode_id} already added to plot {plot_id}",
                error_code="IRRIGATION_MODE_ALREADY_ADDED",
                details={
                    "plot_id": str(plot_id),
                    "irrigation_mode_id": str(irrigation_mode_id)
                }
            )
        
        # Add irrigation mode
        irrigation_mode = PlotIrrigationMode(
            plot_id=plot_id,
            irrigation_mode_id=irrigation_mode_id
        )
        
        self.db.add(irrigation_mode)
        self.db.commit()
        
        logger.info(
            "Added irrigation mode to plot",
            extra={
                "plot_id": str(plot_id),
                "irrigation_mode_id": str(irrigation_mode_id),
                "org_id": str(org_id)
            }
        )
    
    def _to_response(self, plot: Plot) -> PlotResponse:
        """
        Convert plot model to response schema.
        
        Args:
            plot: Plot model
            
        Returns:
            Plot response schema
        """
        # Convert PostGIS geography to GeoJSON
        boundary_geojson = None
        if plot.boundary:
            # Use PostGIS to get GeoJSON directly
            boundary_geojson = self._get_plot_boundary_as_geojson(plot.id)
        
        return PlotResponse(
            id=str(plot.id),
            farm_id=str(plot.farm_id),
            name=plot.name,
            description=plot.description,
            boundary=boundary_geojson,
            area=plot.area,
            area_unit_id=str(plot.area_unit_id) if plot.area_unit_id else None,
            plot_attributes=plot.plot_attributes,
            is_active=plot.is_active,
            created_at=plot.created_at,
            updated_at=plot.updated_at,
            created_by=str(plot.created_by) if plot.created_by else None,
            updated_by=str(plot.updated_by) if plot.updated_by else None
        )
    
    def _get_boundary_as_geojson(self, farm_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get farm boundary as GeoJSON using PostGIS ST_AsGeoJSON.
        
        Args:
            farm_id: Farm ID
            
        Returns:
            GeoJSON Polygon object or None
        """
        from sqlalchemy import text
        
        result = self.db.execute(
            text("SELECT ST_AsGeoJSON(boundary) FROM farms WHERE id = :farm_id"),
            {"farm_id": str(farm_id)}
        ).fetchone()
        
        if result and result[0]:
            return json.loads(result[0])
        return None
    
    def _get_plot_boundary_as_geojson(self, plot_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get plot boundary as GeoJSON using PostGIS ST_AsGeoJSON.
        
        Args:
            plot_id: Plot ID
            
        Returns:
            GeoJSON Polygon object or None
        """
        from sqlalchemy import text
        
        result = self.db.execute(
            text("SELECT ST_AsGeoJSON(boundary) FROM plots WHERE id = :plot_id"),
            {"plot_id": str(plot_id)}
        ).fetchone()
        
        if result and result[0]:
            return json.loads(result[0])
        return None
    
    def _wkt_to_geojson_polygon(self, wkt: str) -> Dict[str, Any]:
        """
        Convert WKT POLYGON to GeoJSON Polygon.
        
        Args:
            wkt: WKT string (e.g., "POLYGON((lon1 lat1, lon2 lat2, ...))")
            
        Returns:
            GeoJSON Polygon object
        """
        # Simple WKT parser for POLYGON
        # Format: POLYGON((lon1 lat1, lon2 lat2, ...))
        coords_str = wkt.replace("POLYGON((", "").replace("))", "")
        points = coords_str.split(", ")
        
        coordinates = []
        for point in points:
            lon, lat = map(float, point.split())
            coordinates.append([lon, lat])
        
        return {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
