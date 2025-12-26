"""
Measurement Unit service for managing units and conversions.
"""
from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from app.models.measurement_unit import MeasurementUnit, MeasurementUnitTranslation
from app.models.enums import MeasurementUnitCategory
from app.schemas.measurement_unit import MeasurementUnitResponse

logger = get_logger(__name__)


class MeasurementUnitService:
    """Service for measurement unit operations and conversions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_units_by_category(
        self, 
        category: MeasurementUnitCategory, 
        language: str = "en"
    ) -> List[MeasurementUnitResponse]:
        """
        Get all measurement units for a specific category.
        
        Args:
            category: Unit category (AREA, VOLUME, WEIGHT, LENGTH, COUNT)
            language: Language code for translations (default: en)
            
        Returns:
            List of measurement units with translations
        """
        units = (
            self.db.query(MeasurementUnit)
            .filter(MeasurementUnit.category == category)
            .order_by(MeasurementUnit.sort_order, MeasurementUnit.code)
            .all()
        )
        
        result = []
        for unit in units:
            # Get translation for requested language
            translation = next(
                (t for t in unit.translations if t.language_code == language),
                None
            )
            
            # Fallback to English if translation not found
            if not translation:
                translation = next(
                    (t for t in unit.translations if t.language_code == "en"),
                    None
                )
            
            result.append(MeasurementUnitResponse(
                id=unit.id,
                category=unit.category,
                code=unit.code,
                symbol=unit.symbol,
                is_base_unit=unit.is_base_unit,
                conversion_factor=unit.conversion_factor,
                sort_order=unit.sort_order,
                name=translation.name if translation else unit.code,
                description=translation.description if translation else None
            ))
        
        logger.info(
            "Retrieved measurement units by category",
            extra={
                "category": category.value,
                "language": language,
                "count": len(result)
            }
        )
        
        return result
    
    def get_unit_by_id(
        self, 
        unit_id: UUID, 
        language: str = "en"
    ) -> MeasurementUnitResponse:
        """
        Get a measurement unit by ID.
        
        Args:
            unit_id: Unit ID
            language: Language code for translations (default: en)
            
        Returns:
            Measurement unit with translation
            
        Raises:
            NotFoundError: If unit not found
        """
        unit = (
            self.db.query(MeasurementUnit)
            .filter(MeasurementUnit.id == unit_id)
            .first()
        )
        
        if not unit:
            raise NotFoundError(
                message=f"Measurement unit {unit_id} not found",
                error_code="MEASUREMENT_UNIT_NOT_FOUND",
                details={"unit_id": str(unit_id)}
            )
        
        # Get translation for requested language
        translation = next(
            (t for t in unit.translations if t.language_code == language),
            None
        )
        
        # Fallback to English if translation not found
        if not translation:
            translation = next(
                (t for t in unit.translations if t.language_code == "en"),
                None
            )
        
        logger.info(
            "Retrieved measurement unit by ID",
            extra={
                "unit_id": str(unit_id),
                "code": unit.code,
                "language": language
            }
        )
        
        return MeasurementUnitResponse(
            id=unit.id,
            category=unit.category,
            code=unit.code,
            symbol=unit.symbol,
            is_base_unit=unit.is_base_unit,
            conversion_factor=unit.conversion_factor,
            sort_order=unit.sort_order,
            name=translation.name if translation else unit.code,
            description=translation.description if translation else None
        )
    
    def get_base_unit_for_category(
        self, 
        category: MeasurementUnitCategory
    ) -> MeasurementUnit:
        """
        Get the base unit for a category.
        
        Args:
            category: Unit category
            
        Returns:
            Base measurement unit
            
        Raises:
            NotFoundError: If base unit not found
        """
        base_unit = (
            self.db.query(MeasurementUnit)
            .filter(
                and_(
                    MeasurementUnit.category == category,
                    MeasurementUnit.is_base_unit == True
                )
            )
            .first()
        )
        
        if not base_unit:
            raise NotFoundError(
                message=f"Base unit not found for category {category.value}",
                error_code="BASE_UNIT_NOT_FOUND",
                details={"category": category.value}
            )
        
        logger.info(
            "Retrieved base unit for category",
            extra={
                "category": category.value,
                "base_unit_code": base_unit.code
            }
        )
        
        return base_unit
    
    def convert_quantity(
        self, 
        value: Decimal, 
        from_unit_id: UUID, 
        to_unit_id: UUID
    ) -> Decimal:
        """
        Convert a quantity from one unit to another.
        
        Args:
            value: Quantity value to convert
            from_unit_id: Source unit ID
            to_unit_id: Target unit ID
            
        Returns:
            Converted quantity value
            
        Raises:
            NotFoundError: If units not found
            ValidationError: If units are from different categories
        """
        # Get both units
        from_unit = self.db.query(MeasurementUnit).filter(
            MeasurementUnit.id == from_unit_id
        ).first()
        
        if not from_unit:
            raise NotFoundError(
                message=f"Source unit {from_unit_id} not found",
                error_code="SOURCE_UNIT_NOT_FOUND",
                details={"from_unit_id": str(from_unit_id)}
            )
        
        to_unit = self.db.query(MeasurementUnit).filter(
            MeasurementUnit.id == to_unit_id
        ).first()
        
        if not to_unit:
            raise NotFoundError(
                message=f"Target unit {to_unit_id} not found",
                error_code="TARGET_UNIT_NOT_FOUND",
                details={"to_unit_id": str(to_unit_id)}
            )
        
        # Validate units are in same category
        if from_unit.category != to_unit.category:
            raise ValidationError(
                message=f"Cannot convert between different unit categories: {from_unit.category.value} and {to_unit.category.value}",
                error_code="INCOMPATIBLE_UNIT_CATEGORIES",
                details={
                    "from_category": from_unit.category.value,
                    "to_category": to_unit.category.value
                }
            )
        
        # Convert to base unit first, then to target unit
        # value_in_base = value * from_unit.conversion_factor
        # result = value_in_base / to_unit.conversion_factor
        
        value_in_base = value * from_unit.conversion_factor
        result = value_in_base / to_unit.conversion_factor
        
        logger.info(
            "Converted quantity",
            extra={
                "value": float(value),
                "from_unit": from_unit.code,
                "to_unit": to_unit.code,
                "result": float(result),
                "category": from_unit.category.value
            }
        )
        
        return result
    
    def convert_to_base_unit(
        self, 
        value: Decimal, 
        unit_id: UUID
    ) -> Decimal:
        """
        Convert a quantity to the base unit of its category.
        
        Args:
            value: Quantity value to convert
            unit_id: Source unit ID
            
        Returns:
            Value in base unit
            
        Raises:
            NotFoundError: If unit not found
        """
        unit = self.db.query(MeasurementUnit).filter(
            MeasurementUnit.id == unit_id
        ).first()
        
        if not unit:
            raise NotFoundError(
                message=f"Unit {unit_id} not found",
                error_code="UNIT_NOT_FOUND",
                details={"unit_id": str(unit_id)}
            )
        
        # If already base unit, return as-is
        if unit.is_base_unit:
            return value
        
        # Convert to base unit
        result = value * unit.conversion_factor
        
        logger.info(
            "Converted to base unit",
            extra={
                "value": float(value),
                "unit": unit.code,
                "result": float(result),
                "category": unit.category.value
            }
        )
        
        return result
    
    def convert_from_base_unit(
        self, 
        value: Decimal, 
        unit_id: UUID
    ) -> Decimal:
        """
        Convert a quantity from the base unit to a specific unit.
        
        Args:
            value: Quantity value in base unit
            unit_id: Target unit ID
            
        Returns:
            Value in target unit
            
        Raises:
            NotFoundError: If unit not found
        """
        unit = self.db.query(MeasurementUnit).filter(
            MeasurementUnit.id == unit_id
        ).first()
        
        if not unit:
            raise NotFoundError(
                message=f"Unit {unit_id} not found",
                error_code="UNIT_NOT_FOUND",
                details={"unit_id": str(unit_id)}
            )
        
        # If already base unit, return as-is
        if unit.is_base_unit:
            return value
        
        # Convert from base unit
        result = value / unit.conversion_factor
        
        logger.info(
            "Converted from base unit",
            extra={
                "value": float(value),
                "unit": unit.code,
                "result": float(result),
                "category": unit.category.value
            }
        )
        
        return result
