"""
Farm service for managing farms with GIS support and ownership validation.
"""
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
import json

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.models.farm import (
    Farm, FarmSupervisor, FarmWaterSource, FarmSoilType, FarmIrrigationMode
)
from app.models.work_order import WorkOrder, WorkOrderScope
from app.models.enums import WorkOrderStatus, WorkOrderScopeType
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse, FarmSupervisorResponse
from app.services.spatial_service import SpatialService

logger = get_logger(__name__)


class FarmService:
    """Service for farm operations with GIS support."""
    
    def __init__(self, db: Session):
        self.db = db
        self.spatial_service = SpatialService(db)
    
    def create_farm(
        self,
        data: FarmCreate,
        org_id: UUID,
        user_id: UUID
    ) -> FarmResponse:
        """
        Create a new farm with GIS validation.
        
        Args:
            data: Farm creation data
            org_id: Organization ID
            user_id: User ID creating the farm
            
        Returns:
            Created farm
            
        Raises:
            ValidationError: If boundary or location is invalid
        """
        # Validate location coordinates
        location_coords = data.location.coordinates
        lon, lat = location_coords
        self.spatial_service.validate_coordinates(lat, lon)
        
        # Validate boundary if provided
        if data.boundary:
            self.spatial_service.validate_boundary(data.boundary.dict())
        
        # Convert GeoJSON to WKT for PostGIS
        location_wkt = self.spatial_service.create_point(lat, lon)
        
        boundary_wkt = None
        if data.boundary:
            boundary_coords = data.boundary.coordinates[0]
            boundary_wkt = self.spatial_service.create_polygon(boundary_coords)
        
        # Calculate area if boundary provided and area not specified
        calculated_area = None
        if data.boundary and not data.area:
            calculated_area = self.spatial_service.calculate_area(data.boundary.dict())
        
        # Create farm
        farm = Farm(
            organization_id=org_id,
            name=data.name,
            description=data.description,
            address=data.address,
            city=data.city,
            district=data.district,
            state=data.state,
            pincode=data.pincode,
            location=location_wkt,
            boundary=boundary_wkt,
            area=data.area or calculated_area,
            area_unit_id=data.area_unit_id,
            farm_attributes=data.farm_attributes or {},
            manager_id=data.manager_id,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(farm)
        self.db.flush()  # Flush to get farm.id
        
        # Add water sources if provided
        if data.water_source_ids:
            for water_source_id in data.water_source_ids:
                water_source = FarmWaterSource(
                    farm_id=farm.id,
                    water_source_id=water_source_id
                )
                self.db.add(water_source)
        
        # Add soil types if provided
        if data.soil_type_ids:
            for soil_type_id in data.soil_type_ids:
                soil_type = FarmSoilType(
                    farm_id=farm.id,
                    soil_type_id=soil_type_id
                )
                self.db.add(soil_type)
        
        # Add irrigation modes if provided
        if data.irrigation_mode_ids:
            for irrigation_mode_id in data.irrigation_mode_ids:
                irrigation_mode = FarmIrrigationMode(
                    farm_id=farm.id,
                    irrigation_mode_id=irrigation_mode_id
                )
                self.db.add(irrigation_mode)
        
        self.db.commit()
        self.db.refresh(farm)
        
        logger.info(
            "Created farm",
            extra={
                "farm_id": str(farm.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "name": data.name,
                "has_boundary": boundary_wkt is not None,
                "area": float(farm.area) if farm.area else None
            }
        )
        
        return self._to_response(farm)
    
    def get_farms(
        self,
        org_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[FarmResponse], int]:
        """
        Get farms for an organization with pagination.
        
        Args:
            org_id: Organization ID
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            
        Returns:
            Tuple of (list of farms, total count)
        """
        offset = (page - 1) * limit
        
        # Query farms
        query = (
            self.db.query(Farm)
            .filter(
                and_(
                    Farm.organization_id == org_id,
                    Farm.is_active == True
                )
            )
            .order_by(Farm.created_at.desc())
        )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        farms = query.offset(offset).limit(limit).all()
        
        logger.info(
            "Retrieved farms",
            extra={
                "org_id": str(org_id),
                "page": page,
                "limit": limit,
                "count": len(farms),
                "total": total
            }
        )
        
        return [self._to_response(farm) for farm in farms], total
    
    def get_farm_by_id(
        self,
        farm_id: UUID,
        org_id: UUID
    ) -> FarmResponse:
        """
        Get farm by ID with ownership validation.
        Also allows FSP access if valid Work Order exists.
        
        Args:
            farm_id: Farm ID
            org_id: Organization ID (Farming OR FSP)
            
        Returns:
            Farm details
            
        Raises:
            NotFoundError: If farm not found or not accessible
        """
        # 1. Try finding farm directly owned by org
        farm = (
            self.db.query(Farm)
            .options(
                joinedload(Farm.manager),
                joinedload(Farm.supervisors),
                joinedload(Farm.water_sources),
                joinedload(Farm.soil_types),
                joinedload(Farm.irrigation_modes),
                joinedload(Farm.area_unit)
            )
            .filter(
                and_(
                    Farm.id == farm_id,
                    Farm.is_active == True
                )
            )
            .first()
        )
        
        if not farm:
           raise NotFoundError(
                message=f"Farm {farm_id} not found",
                error_code="FARM_NOT_FOUND",
                details={"farm_id": str(farm_id)}
            )

        # 2. Check Permission
        has_access = False
        
        # A. Direct Ownership
        if farm.organization_id == org_id:
            has_access = True
            
        # B. FSP Work Order Access
        if not has_access:
            print(f"DEBUG: Checking FSP Access for Farm {farm_id}, Req Org {org_id}, Farm Org {farm.organization_id}")
            # Check for active work orders where FSP Org = org_id AND Farming Org = farm.organization_id
            work_order = self.db.query(WorkOrder).filter(
                WorkOrder.fsp_organization_id == org_id,
                WorkOrder.farming_organization_id == farm.organization_id,
                WorkOrder.status.in_([WorkOrderStatus.ACTIVE, WorkOrderStatus.ACCEPTED])
            ).first()
            
            print(f"DEBUG: Work Order found: {work_order}")
            
            if work_order:
                # Check Scope (Optional: For now, strict farm scope or organization wide?)
                # Requirement implies implicit access to farm if working on it. 
                # Strict check: Does strict scope exist?
                # Simplify scope check: specific farm scope OR organization wide
                scope_items = self.db.query(WorkOrderScope).filter(
                    WorkOrderScope.work_order_id == work_order.id
                ).all()
                
                print(f"DEBUG: Scope items count: {len(scope_items)}")
                
                for item in scope_items:
                    print(f"DEBUG: Checking item scope={item.scope}, scope_id={item.scope_id}")
                    if item.scope == WorkOrderScopeType.ORGANIZATION:
                        has_access = True
                        break
                    
                    if item.scope == WorkOrderScopeType.FARM and str(item.scope_id) == str(farm_id):
                        has_access = True
                        break

        if not has_access:
             raise NotFoundError(
                message=f"Farm {farm_id} not found",
                error_code="FARM_NOT_FOUND",
                details={"farm_id": str(farm_id)}
            )
        
        logger.info(
            "Retrieved farm by ID",
            extra={
                "farm_id": str(farm_id),
                "org_id": str(org_id),
                "is_fsp_access": farm.organization_id != org_id
            }
        )
        
        return self._to_response(farm)
    
    def update_farm(
        self,
        farm_id: UUID,
        data: FarmUpdate,
        org_id: UUID,
        user_id: UUID
    ) -> FarmResponse:
        """
        Update farm with GIS validation.
        
        Args:
            farm_id: Farm ID
            data: Farm update data
            org_id: Organization ID
            user_id: User ID updating the farm
            
        Returns:
            Updated farm
            
        Raises:
            NotFoundError: If farm not found
            ValidationError: If boundary or location is invalid
        """
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
        
        # Update basic fields
        if data.name is not None:
            farm.name = data.name
        if data.description is not None:
            farm.description = data.description
        if data.address is not None:
            farm.address = data.address
        if data.city is not None:
            farm.city = data.city
        if data.district is not None:
            farm.district = data.district
        if data.state is not None:
            farm.state = data.state
        if data.pincode is not None:
            farm.pincode = data.pincode
        if data.manager_id is not None:
            farm.manager_id = data.manager_id
        if data.is_active is not None:
            farm.is_active = data.is_active
        
        # Update location if provided
        if data.location:
            location_coords = data.location.coordinates
            lon, lat = location_coords
            self.spatial_service.validate_coordinates(lat, lon)
            farm.location = self.spatial_service.create_point(lat, lon)
        
        # Update boundary if provided
        if data.boundary:
            self.spatial_service.validate_boundary(data.boundary.dict())
            boundary_coords = data.boundary.coordinates[0]
            farm.boundary = self.spatial_service.create_polygon(boundary_coords)
            
            # Recalculate area if boundary changed and area not explicitly provided
            if data.area is None:
                calculated_area = self.spatial_service.calculate_area(data.boundary.dict())
                farm.area = calculated_area
        
        # Update area if provided
        if data.area is not None:
            farm.area = data.area
        if data.area_unit_id is not None:
            farm.area_unit_id = data.area_unit_id
        
        # Update farm attributes
        if data.farm_attributes is not None:
            farm.farm_attributes = data.farm_attributes
        
        # Update water sources if provided
        if data.water_source_ids is not None:
            # Remove existing water sources
            self.db.query(FarmWaterSource).filter(
                FarmWaterSource.farm_id == farm_id
            ).delete(synchronize_session=False)
            self.db.flush()  # Ensure deletion is executed before adding new ones
            
            # Add new water sources
            for water_source_id in data.water_source_ids:
                water_source = FarmWaterSource(
                    farm_id=farm_id,
                    water_source_id=water_source_id
                )
                self.db.add(water_source)
        
        # Update soil types if provided
        if data.soil_type_ids is not None:
            # Remove existing soil types
            self.db.query(FarmSoilType).filter(
                FarmSoilType.farm_id == farm_id
            ).delete(synchronize_session=False)
            self.db.flush()  # Ensure deletion is executed before adding new ones
            
            # Add new soil types
            for soil_type_id in data.soil_type_ids:
                soil_type = FarmSoilType(
                    farm_id=farm_id,
                    soil_type_id=soil_type_id
                )
                self.db.add(soil_type)
        
        # Update irrigation modes if provided
        if data.irrigation_mode_ids is not None:
            # Remove existing irrigation modes
            self.db.query(FarmIrrigationMode).filter(
                FarmIrrigationMode.farm_id == farm_id
            ).delete(synchronize_session=False)
            self.db.flush()  # Ensure deletion is executed before adding new ones
            
            # Add new irrigation modes
            for irrigation_mode_id in data.irrigation_mode_ids:
                irrigation_mode = FarmIrrigationMode(
                    farm_id=farm_id,
                    irrigation_mode_id=irrigation_mode_id
                )
                self.db.add(irrigation_mode)
        
        farm.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(farm)
        
        logger.info(
            "Updated farm",
            extra={
                "farm_id": str(farm_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_response(farm)
    
    def delete_farm(
        self,
        farm_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) farm.
        
        Args:
            farm_id: Farm ID
            org_id: Organization ID
            user_id: User ID deleting the farm
            
        Raises:
            NotFoundError: If farm not found
        """
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
        
        # Soft delete
        farm.is_active = False
        farm.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted farm",
            extra={
                "farm_id": str(farm_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def assign_supervisor(
        self,
        farm_id: UUID,
        supervisor_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> FarmSupervisorResponse:
        """
        Assign supervisor to farm.
        
        Args:
            farm_id: Farm ID
            supervisor_id: Supervisor user ID
            org_id: Organization ID
            user_id: User ID assigning the supervisor
            
        Returns:
            Farm supervisor record
            
        Raises:
            NotFoundError: If farm not found
            ValidationError: If supervisor already assigned
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
        
        # Check if supervisor already assigned
        existing = self.db.query(FarmSupervisor).filter(
            and_(
                FarmSupervisor.farm_id == farm_id,
                FarmSupervisor.supervisor_id == supervisor_id
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Supervisor {supervisor_id} already assigned to farm {farm_id}",
                error_code="SUPERVISOR_ALREADY_ASSIGNED",
                details={
                    "farm_id": str(farm_id),
                    "supervisor_id": str(supervisor_id)
                }
            )
        
        # Create supervisor assignment
        supervisor = FarmSupervisor(
            farm_id=farm_id,
            supervisor_id=supervisor_id,
            assigned_by=user_id
        )
        
        self.db.add(supervisor)
        self.db.commit()
        self.db.refresh(supervisor)
        
        logger.info(
            "Assigned supervisor to farm",
            extra={
                "farm_id": str(farm_id),
                "supervisor_id": str(supervisor_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return FarmSupervisorResponse.from_orm(supervisor)
    
    def remove_supervisor(
        self,
        farm_id: UUID,
        supervisor_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Remove supervisor from farm.
        
        Args:
            farm_id: Farm ID
            supervisor_id: Supervisor user ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If farm or supervisor assignment not found
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
        
        # Find supervisor assignment
        supervisor = self.db.query(FarmSupervisor).filter(
            and_(
                FarmSupervisor.farm_id == farm_id,
                FarmSupervisor.supervisor_id == supervisor_id
            )
        ).first()
        
        if not supervisor:
            raise NotFoundError(
                message=f"Supervisor {supervisor_id} not assigned to farm {farm_id}",
                error_code="SUPERVISOR_NOT_FOUND",
                details={
                    "farm_id": str(farm_id),
                    "supervisor_id": str(supervisor_id)
                }
            )
        
        # Delete supervisor assignment
        self.db.delete(supervisor)
        self.db.commit()
        
        logger.info(
            "Removed supervisor from farm",
            extra={
                "farm_id": str(farm_id),
                "supervisor_id": str(supervisor_id),
                "org_id": str(org_id)
            }
        )
    
    def add_water_source(
        self,
        farm_id: UUID,
        water_source_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Add water source to farm.
        
        Args:
            farm_id: Farm ID
            water_source_id: Water source reference data ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If farm not found
            ValidationError: If water source already added
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
        
        # Check if water source already added
        existing = self.db.query(FarmWaterSource).filter(
            and_(
                FarmWaterSource.farm_id == farm_id,
                FarmWaterSource.water_source_id == water_source_id
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Water source {water_source_id} already added to farm {farm_id}",
                error_code="WATER_SOURCE_ALREADY_ADDED",
                details={
                    "farm_id": str(farm_id),
                    "water_source_id": str(water_source_id)
                }
            )
        
        # Add water source
        water_source = FarmWaterSource(
            farm_id=farm_id,
            water_source_id=water_source_id
        )
        
        self.db.add(water_source)
        self.db.commit()
        
        logger.info(
            "Added water source to farm",
            extra={
                "farm_id": str(farm_id),
                "water_source_id": str(water_source_id),
                "org_id": str(org_id)
            }
        )
    
    def add_soil_type(
        self,
        farm_id: UUID,
        soil_type_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Add soil type to farm.
        
        Args:
            farm_id: Farm ID
            soil_type_id: Soil type reference data ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If farm not found
            ValidationError: If soil type already added
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
        
        # Check if soil type already added
        existing = self.db.query(FarmSoilType).filter(
            and_(
                FarmSoilType.farm_id == farm_id,
                FarmSoilType.soil_type_id == soil_type_id
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Soil type {soil_type_id} already added to farm {farm_id}",
                error_code="SOIL_TYPE_ALREADY_ADDED",
                details={
                    "farm_id": str(farm_id),
                    "soil_type_id": str(soil_type_id)
                }
            )
        
        # Add soil type
        soil_type = FarmSoilType(
            farm_id=farm_id,
            soil_type_id=soil_type_id
        )
        
        self.db.add(soil_type)
        self.db.commit()
        
        logger.info(
            "Added soil type to farm",
            extra={
                "farm_id": str(farm_id),
                "soil_type_id": str(soil_type_id),
                "org_id": str(org_id)
            }
        )
    
    def add_irrigation_mode(
        self,
        farm_id: UUID,
        irrigation_mode_id: UUID,
        org_id: UUID
    ) -> None:
        """
        Add irrigation mode to farm.
        
        Args:
            farm_id: Farm ID
            irrigation_mode_id: Irrigation mode reference data ID
            org_id: Organization ID
            
        Raises:
            NotFoundError: If farm not found
            ValidationError: If irrigation mode already added
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
        
        # Check if irrigation mode already added
        existing = self.db.query(FarmIrrigationMode).filter(
            and_(
                FarmIrrigationMode.farm_id == farm_id,
                FarmIrrigationMode.irrigation_mode_id == irrigation_mode_id
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Irrigation mode {irrigation_mode_id} already added to farm {farm_id}",
                error_code="IRRIGATION_MODE_ALREADY_ADDED",
                details={
                    "farm_id": str(farm_id),
                    "irrigation_mode_id": str(irrigation_mode_id)
                }
            )
        
        # Add irrigation mode
        irrigation_mode = FarmIrrigationMode(
            farm_id=farm_id,
            irrigation_mode_id=irrigation_mode_id
        )
        
        self.db.add(irrigation_mode)
        self.db.commit()
        
        logger.info(
            "Added irrigation mode to farm",
            extra={
                "farm_id": str(farm_id),
                "irrigation_mode_id": str(irrigation_mode_id),
                "org_id": str(org_id)
            }
        )
    
    def _to_response(self, farm: Farm) -> FarmResponse:
        """
        Convert farm model to response schema.
        
        Args:
            farm: Farm model
            
        Returns:
            Farm response schema
        """
        # Convert PostGIS geography to GeoJSON
        from sqlalchemy import func
        
        location_geojson = None
        if farm.location:
            # Use PostGIS ST_AsText to convert binary to WKT
            wkt_location = self.db.scalar(func.ST_AsText(farm.location))
            if wkt_location:
                location_geojson = self._wkt_to_geojson_point(wkt_location)
        
        boundary_geojson = None
        if farm.boundary:
            # Use PostGIS ST_AsText to convert binary to WKT
            wkt_boundary = self.db.scalar(func.ST_AsText(farm.boundary))
            if wkt_boundary:
                boundary_geojson = self._wkt_to_geojson_polygon(wkt_boundary)
        
        # Ensure relationships are loaded with reference data
        from app.models.reference_data import ReferenceData
        from app.schemas.farm import FarmWaterSourceResponse, FarmSoilTypeResponse, FarmIrrigationModeResponse, ReferenceDataNested
        
        if not hasattr(farm, 'water_sources') or farm.water_sources is None:
            from app.models.reference_data import ReferenceDataTranslation
            farm.water_sources = (
                self.db.query(FarmWaterSource)
                .options(
                    joinedload(FarmWaterSource.water_source)
                    .joinedload('translations')
                )
                .filter(FarmWaterSource.farm_id == farm.id)
                .all()
            )
        
        if not hasattr(farm, 'soil_types') or farm.soil_types is None:
            farm.soil_types = (
                self.db.query(FarmSoilType)
                .options(
                    joinedload(FarmSoilType.soil_type)
                    .joinedload('translations')
                )
                .filter(FarmSoilType.farm_id == farm.id)
                .all()
            )
        
        if not hasattr(farm, 'irrigation_modes') or farm.irrigation_modes is None:
            farm.irrigation_modes = (
                self.db.query(FarmIrrigationMode)
                .options(
                    joinedload(FarmIrrigationMode.irrigation_mode)
                    .joinedload('translations')
                )
                .filter(FarmIrrigationMode.farm_id == farm.id)
                .all()
            )
        
        # Extract water sources
        water_source_ids = [str(ws.water_source_id) for ws in farm.water_sources] if farm.water_sources else []
        
        # Extract soil types
        soil_type_ids = [str(st.soil_type_id) for st in farm.soil_types] if farm.soil_types else []
        
        # Extract irrigation modes
        irrigation_mode_ids = [str(im.irrigation_mode_id) for im in farm.irrigation_modes] if farm.irrigation_modes else []
        
        # Convert to response schemas with reference data
        water_sources_response = []
        for ws in farm.water_sources:
            # Get display name from translations (default to English 'en')
            display_name = ws.water_source.code  # Fallback to code
            if ws.water_source.translations:
                # Try to get English translation first
                en_translation = next((t for t in ws.water_source.translations if t.language_code == 'en'), None)
                if en_translation:
                    display_name = en_translation.display_name
                elif ws.water_source.translations:
                    # If no English, use first available translation
                    display_name = ws.water_source.translations[0].display_name
            
            water_sources_response.append(FarmWaterSourceResponse(
                id=str(ws.id),
                farm_id=str(ws.farm_id),
                water_source_id=str(ws.water_source_id),
                created_at=ws.created_at,
                reference_data=ReferenceDataNested(
                    id=str(ws.water_source.id),
                    code=ws.water_source.code,
                    display_name=display_name
                )
            ))
        
        soil_types_response = []
        for st in farm.soil_types:
            # Get display name from translations (default to English 'en')
            display_name = st.soil_type.code  # Fallback to code
            if st.soil_type.translations:
                # Try to get English translation first
                en_translation = next((t for t in st.soil_type.translations if t.language_code == 'en'), None)
                if en_translation:
                    display_name = en_translation.display_name
                elif st.soil_type.translations:
                    # If no English, use first available translation
                    display_name = st.soil_type.translations[0].display_name
            
            soil_types_response.append(FarmSoilTypeResponse(
                id=str(st.id),
                farm_id=str(st.farm_id),
                soil_type_id=str(st.soil_type_id),
                created_at=st.created_at,
                reference_data=ReferenceDataNested(
                    id=str(st.soil_type.id),
                    code=st.soil_type.code,
                    display_name=display_name
                )
            ))
        
        irrigation_modes_response = []
        for im in farm.irrigation_modes:
            # Get display name from translations (default to English 'en')
            display_name = im.irrigation_mode.code  # Fallback to code
            if im.irrigation_mode.translations:
                # Try to get English translation first
                en_translation = next((t for t in im.irrigation_mode.translations if t.language_code == 'en'), None)
                if en_translation:
                    display_name = en_translation.display_name
                elif im.irrigation_mode.translations:
                    # If no English, use first available translation
                    display_name = im.irrigation_mode.translations[0].display_name
            
            irrigation_modes_response.append(FarmIrrigationModeResponse(
                id=str(im.id),
                farm_id=str(im.farm_id),
                irrigation_mode_id=str(im.irrigation_mode_id),
                created_at=im.created_at,
                reference_data=ReferenceDataNested(
                    id=str(im.irrigation_mode.id),
                    code=im.irrigation_mode.code,
                    display_name=display_name
                )
            ))
        
        return FarmResponse(
            id=str(farm.id),
            organization_id=str(farm.organization_id),
            name=farm.name,
            description=farm.description,
            address=farm.address,
            city=farm.city,
            district=farm.district,
            state=farm.state,
            pincode=farm.pincode,
            location=location_geojson,
            boundary=boundary_geojson,
            area=farm.area,
            area_unit_id=str(farm.area_unit_id) if farm.area_unit_id else None,
            farm_attributes=farm.farm_attributes,
            manager_id=str(farm.manager_id) if farm.manager_id else None,
            water_source_ids=water_source_ids,
            soil_type_ids=soil_type_ids,
            irrigation_mode_ids=irrigation_mode_ids,
            water_sources=water_sources_response,
            soil_types=soil_types_response,
            irrigation_modes=irrigation_modes_response,
            is_active=farm.is_active,
            created_at=farm.created_at,
            updated_at=farm.updated_at,
            created_by=str(farm.created_by) if farm.created_by else None,
            updated_by=str(farm.updated_by) if farm.updated_by else None
        )
    
    def _wkt_to_geojson_point(self, wkt: str) -> Dict[str, Any]:
        """
        Convert WKT POINT to GeoJSON Point.
        
        Args:
            wkt: WKT string (e.g., "POINT(lon lat)")
            
        Returns:
            GeoJSON Point object
        """
        # Simple WKT parser for POINT
        # Format: POINT(lon lat)
        coords_str = wkt.replace("POINT(", "").replace(")", "")
        lon, lat = map(float, coords_str.split())
        
        return {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    
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
        # PostGIS may use either space or comma as separator
        coords_str = wkt.replace("POLYGON((", "").replace("))", "")
        points = coords_str.split(",")
        
        coordinates = []
        for point in points:
            # Handle both "lon lat" and "lat,lon" formats
            point = point.strip()
            if " " in point:
                # Format: "lon lat"
                lon, lat = map(float, point.split())
            else:
                # This shouldn't happen with proper WKT, but handle it
                raise ValueError(f"Invalid WKT point format: {point}")
            coordinates.append([lon, lat])
        
        return {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
