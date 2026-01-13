"""
Unit tests for MeasurementUnitService.

Tests:
- get_units_by_category
- convert_quantity
- base unit identification
- multilingual support

Requirements: 1.1, 1.2, 1.3, 1.4
"""
import pytest
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.measurement_unit_service import MeasurementUnitService
from app.models.enums import MeasurementUnitCategory
from app.core.exceptions import NotFoundError, ValidationError


class TestMeasurementUnitService:
    """Test suite for MeasurementUnitService."""
    
    def test_get_units_by_category_area(self, db: Session):
        """Test retrieving area measurement units."""
        service = MeasurementUnitService(db)
        
        # Get area units
        units = service.get_units_by_category(MeasurementUnitCategory.AREA, language="en")
        
        # Verify we got units
        assert len(units) > 0
        
        # Verify all units are area category
        for unit in units:
            assert unit.category == MeasurementUnitCategory.AREA
        
        # Verify expected units exist
        unit_codes = [u.code for u in units]
        assert "SQ_M" in unit_codes
        assert "ACRE" in unit_codes
        assert "HECTARE" in unit_codes
    
    def test_get_units_by_category_weight(self, db: Session):
        """Test retrieving weight measurement units."""
        service = MeasurementUnitService(db)
        
        # Get weight units
        units = service.get_units_by_category(MeasurementUnitCategory.WEIGHT, language="en")
        
        # Verify we got units
        assert len(units) > 0
        
        # Verify all units are weight category
        for unit in units:
            assert unit.category == MeasurementUnitCategory.WEIGHT
        
        # Verify expected units exist
        unit_codes = [u.code for u in units]
        assert "KG" in unit_codes
        assert "GRAM" in unit_codes
        assert "TONNE" in unit_codes
    
    def test_get_units_by_category_volume(self, db: Session):
        """Test retrieving volume measurement units."""
        service = MeasurementUnitService(db)
        
        # Get volume units
        units = service.get_units_by_category(MeasurementUnitCategory.VOLUME, language="en")
        
        # Verify we got units
        assert len(units) > 0
        
        # Verify all units are volume category
        for unit in units:
            assert unit.category == MeasurementUnitCategory.VOLUME
        
        # Verify expected units exist
        unit_codes = [u.code for u in units]
        assert "LITER" in unit_codes
        assert "MILLILITER" in unit_codes
    
    def test_get_units_by_category_multilingual(self, db: Session):
        """Test retrieving units with Tamil translations."""
        service = MeasurementUnitService(db)
        
        # Get units in Tamil
        units_ta = service.get_units_by_category(MeasurementUnitCategory.AREA, language="ta")
        
        # Verify we got units
        assert len(units_ta) > 0
        
        # Find square meter unit
        sq_m_unit = next((u for u in units_ta if u.code == "SQ_M"), None)
        assert sq_m_unit is not None
        
        # Verify Tamil translation exists
        assert sq_m_unit.name == "சதுர மீட்டர்"
    
    def test_get_base_unit_for_category_area(self, db: Session):
        """Test identifying base unit for area category."""
        service = MeasurementUnitService(db)
        
        # Get base unit for area
        base_unit = service.get_base_unit_for_category(MeasurementUnitCategory.AREA)
        
        # Verify it's the correct base unit
        assert base_unit.code == "SQ_M"
        assert base_unit.is_base_unit is True
        assert base_unit.conversion_factor == Decimal("1.0")
    
    def test_get_base_unit_for_category_weight(self, db: Session):
        """Test identifying base unit for weight category."""
        service = MeasurementUnitService(db)
        
        # Get base unit for weight
        base_unit = service.get_base_unit_for_category(MeasurementUnitCategory.WEIGHT)
        
        # Verify it's the correct base unit
        assert base_unit.code == "KG"
        assert base_unit.is_base_unit is True
        assert base_unit.conversion_factor == Decimal("1.0")
    
    def test_get_base_unit_for_category_volume(self, db: Session):
        """Test identifying base unit for volume category."""
        service = MeasurementUnitService(db)
        
        # Get base unit for volume
        base_unit = service.get_base_unit_for_category(MeasurementUnitCategory.VOLUME)
        
        # Verify it's the correct base unit
        assert base_unit.code == "LITER"
        assert base_unit.is_base_unit is True
        assert base_unit.conversion_factor == Decimal("1.0")
    
    def test_convert_quantity_within_same_category(self, db: Session):
        """Test converting quantity between units in same category."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.WEIGHT, language="en")
        kg_unit = next(u for u in units if u.code == "KG")
        gram_unit = next(u for u in units if u.code == "GRAM")
        
        # Convert 1 kg to grams
        result = service.convert_quantity(
            value=Decimal("1.0"),
            from_unit_id=kg_unit.id,
            to_unit_id=gram_unit.id
        )
        
        # 1 kg = 1000 grams
        assert result == Decimal("1000.0")
    
    def test_convert_quantity_kg_to_tonne(self, db: Session):
        """Test converting kilograms to tonnes."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.WEIGHT, language="en")
        kg_unit = next(u for u in units if u.code == "KG")
        tonne_unit = next(u for u in units if u.code == "TONNE")
        
        # Convert 1000 kg to tonnes
        result = service.convert_quantity(
            value=Decimal("1000.0"),
            from_unit_id=kg_unit.id,
            to_unit_id=tonne_unit.id
        )
        
        # 1000 kg = 1 tonne
        assert result == Decimal("1.0")
    
    def test_convert_quantity_area_units(self, db: Session):
        """Test converting area units (acres to hectares)."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.AREA, language="en")
        acre_unit = next(u for u in units if u.code == "ACRE")
        hectare_unit = next(u for u in units if u.code == "HECTARE")
        
        # Convert 1 acre to hectares
        result = service.convert_quantity(
            value=Decimal("1.0"),
            from_unit_id=acre_unit.id,
            to_unit_id=hectare_unit.id
        )
        
        # 1 acre ≈ 0.4047 hectares
        # acre conversion_factor = 4046.86 (to sq_m)
        # hectare conversion_factor = 10000.0 (to sq_m)
        # result = 1 * 4046.86 / 10000.0 = 0.404686
        expected = Decimal("0.404686")
        assert abs(result - expected) < Decimal("0.000001")
    
    def test_convert_quantity_incompatible_categories(self, db: Session):
        """Test that converting between different categories raises error."""
        service = MeasurementUnitService(db)
        
        # Get units from different categories
        area_units = service.get_units_by_category(MeasurementUnitCategory.AREA, language="en")
        weight_units = service.get_units_by_category(MeasurementUnitCategory.WEIGHT, language="en")
        
        acre_unit = next(u for u in area_units if u.code == "ACRE")
        kg_unit = next(u for u in weight_units if u.code == "KG")
        
        # Try to convert area to weight - should fail
        with pytest.raises(ValidationError) as exc_info:
            service.convert_quantity(
                value=Decimal("1.0"),
                from_unit_id=acre_unit.id,
                to_unit_id=kg_unit.id
            )
        
        # Verify error message
        assert "Cannot convert between different unit categories" in str(exc_info.value.message)
        assert exc_info.value.error_code == "INCOMPATIBLE_UNIT_CATEGORIES"
    
    def test_convert_to_base_unit(self, db: Session):
        """Test converting to base unit."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.WEIGHT, language="en")
        gram_unit = next(u for u in units if u.code == "GRAM")
        
        # Convert 500 grams to base unit (kg)
        result = service.convert_to_base_unit(
            value=Decimal("500.0"),
            unit_id=gram_unit.id
        )
        
        # 500 grams = 0.5 kg
        assert result == Decimal("0.5")
    
    def test_convert_from_base_unit(self, db: Session):
        """Test converting from base unit."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.WEIGHT, language="en")
        gram_unit = next(u for u in units if u.code == "GRAM")
        
        # Convert 2 kg (base unit) to grams
        result = service.convert_from_base_unit(
            value=Decimal("2.0"),
            unit_id=gram_unit.id
        )
        
        # 2 kg = 2000 grams
        assert result == Decimal("2000.0")
    
    def test_get_unit_by_id(self, db: Session):
        """Test retrieving a unit by ID."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.AREA, language="en")
        acre_unit = units[0]
        
        # Get unit by ID
        retrieved_unit = service.get_unit_by_id(acre_unit.id, language="en")
        
        # Verify it's the same unit
        assert retrieved_unit.id == acre_unit.id
        assert retrieved_unit.code == acre_unit.code
        assert retrieved_unit.category == acre_unit.category
    
    def test_get_unit_by_id_not_found(self, db: Session):
        """Test that getting non-existent unit raises error."""
        service = MeasurementUnitService(db)
        
        # Try to get unit with random UUID
        fake_id = UUID("00000000-0000-0000-0000-000000000000")
        
        with pytest.raises(NotFoundError) as exc_info:
            service.get_unit_by_id(fake_id, language="en")
        
        # Verify error
        assert exc_info.value.error_code == "MEASUREMENT_UNIT_NOT_FOUND"
    
    def test_units_sorted_by_sort_order(self, db: Session):
        """Test that units are returned in correct sort order."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.AREA, language="en")
        
        # Verify they are sorted
        for i in range(len(units) - 1):
            assert units[i].sort_order <= units[i + 1].sort_order
    
    def test_conversion_accuracy(self, db: Session):
        """Test conversion accuracy with decimal precision."""
        service = MeasurementUnitService(db)
        
        # Get units
        units = service.get_units_by_category(MeasurementUnitCategory.AREA, language="en")
        sq_m_unit = next(u for u in units if u.code == "SQ_M")
        cent_unit = next(u for u in units if u.code == "CENT")
        
        # Convert 100 sq meters to cents
        result = service.convert_quantity(
            value=Decimal("100.0"),
            from_unit_id=sq_m_unit.id,
            to_unit_id=cent_unit.id
        )
        
        # 100 sq_m = 100 / 40.4686 cents ≈ 2.471 cents
        expected = Decimal("100.0") / Decimal("40.4686")
        
        # Verify precision (within 0.0001)
        assert abs(result - expected) < Decimal("0.0001")
