"""
Unit tests for SpatialService.

Tests GIS operations including coordinate validation, boundary validation,
plot containment checks, and area calculations.

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7
"""
import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.spatial_service import SpatialService
from app.core.exceptions import ValidationError


class TestValidateCoordinates:
    """Test coordinate validation."""
    
    def test_valid_coordinates(self, db: Session):
        """Test validation of valid coordinates."""
        service = SpatialService(db)
        
        # Valid coordinates
        assert service.validate_coordinates(0, 0) is True
        assert service.validate_coordinates(45.5, -122.6) is True
        assert service.validate_coordinates(-33.8, 151.2) is True
        assert service.validate_coordinates(90, 180) is True
        assert service.validate_coordinates(-90, -180) is True
    
    def test_invalid_latitude_too_high(self, db: Session):
        """Test validation fails for latitude > 90."""
        service = SpatialService(db)
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_coordinates(91, 0)
        
        assert exc_info.value.error_code == "INVALID_LATITUDE"
        assert "91" in exc_info.value.message
    
    def test_invalid_latitude_too_low(self, db: Session):
        """Test validation fails for latitude < -90."""
        service = SpatialService(db)
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_coordinates(-91, 0)
        
        assert exc_info.value.error_code == "INVALID_LATITUDE"
        assert "-91" in exc_info.value.message
    
    def test_invalid_longitude_too_high(self, db: Session):
        """Test validation fails for longitude > 180."""
        service = SpatialService(db)
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_coordinates(0, 181)
        
        assert exc_info.value.error_code == "INVALID_LONGITUDE"
        assert "181" in exc_info.value.message
    
    def test_invalid_longitude_too_low(self, db: Session):
        """Test validation fails for longitude < -180."""
        service = SpatialService(db)
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_coordinates(0, -181)
        
        assert exc_info.value.error_code == "INVALID_LONGITUDE"
        assert "-181" in exc_info.value.message


class TestValidateBoundary:
    """Test boundary validation."""
    
    def test_valid_boundary(self, db: Session):
        """Test validation of valid GeoJSON boundary."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1],
                [1, 1],
                [1, 0],
                [0, 0]  # Closed polygon
            ]]
        }
        
        assert service.validate_boundary(boundary) is True
    
    def test_empty_boundary(self, db: Session):
        """Test validation fails for empty boundary."""
        service = SpatialService(db)
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_boundary(None)
        
        assert exc_info.value.error_code == "EMPTY_BOUNDARY"
    
    def test_invalid_boundary_type(self, db: Session):
        """Test validation fails for non-Polygon type."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Point",
            "coordinates": [0, 0]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_boundary(boundary)
        
        assert exc_info.value.error_code == "INVALID_BOUNDARY_TYPE"
    
    def test_empty_coordinates(self, db: Session):
        """Test validation fails for empty coordinates."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_boundary(boundary)
        
        assert exc_info.value.error_code == "EMPTY_COORDINATES"
    
    def test_insufficient_points(self, db: Session):
        """Test validation fails for polygon with < 4 points."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1],
                [0, 0]  # Only 3 points
            ]]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_boundary(boundary)
        
        assert exc_info.value.error_code == "INSUFFICIENT_POINTS"
    
    def test_polygon_not_closed(self, db: Session):
        """Test validation fails for non-closed polygon."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1],
                [1, 1],
                [1, 0]  # Not closed (should end with [0, 0])
            ]]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_boundary(boundary)
        
        assert exc_info.value.error_code == "POLYGON_NOT_CLOSED"
    
    def test_invalid_coordinate_format(self, db: Session):
        """Test validation fails for invalid coordinate format."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1, 2],  # 3 values instead of 2
                [1, 1],
                [1, 0],
                [0, 0]
            ]]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_boundary(boundary)
        
        assert exc_info.value.error_code == "INVALID_COORDINATE_FORMAT"
    
    def test_invalid_coordinates_out_of_range(self, db: Session):
        """Test validation fails for coordinates out of valid range."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 91],  # Invalid latitude
                [1, 1],
                [1, 0],
                [0, 0]
            ]]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_boundary(boundary)
        
        assert exc_info.value.error_code == "INVALID_LATITUDE"


class TestValidatePlotWithinFarm:
    """Test plot containment validation."""
    
    def test_plot_within_farm(self, db: Session):
        """Test validation succeeds when plot is within farm."""
        service = SpatialService(db)
        
        # Farm boundary (larger)
        farm_boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 10],
                [10, 10],
                [10, 0],
                [0, 0]
            ]]
        }
        
        # Plot boundary (smaller, inside farm)
        plot_boundary = {
            "type": "Polygon",
            "coordinates": [[
                [2, 2],
                [2, 5],
                [5, 5],
                [5, 2],
                [2, 2]
            ]]
        }
        
        assert service.validate_plot_within_farm(plot_boundary, farm_boundary) is True
    
    def test_plot_outside_farm(self, db: Session):
        """Test validation fails when plot is outside farm."""
        service = SpatialService(db)
        
        # Farm boundary
        farm_boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 10],
                [10, 10],
                [10, 0],
                [0, 0]
            ]]
        }
        
        # Plot boundary (outside farm)
        plot_boundary = {
            "type": "Polygon",
            "coordinates": [[
                [15, 15],
                [15, 20],
                [20, 20],
                [20, 15],
                [15, 15]
            ]]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_plot_within_farm(plot_boundary, farm_boundary)
        
        assert exc_info.value.error_code == "PLOT_OUTSIDE_FARM"
    
    def test_plot_partially_outside_farm(self, db: Session):
        """Test validation fails when plot partially overlaps farm boundary."""
        service = SpatialService(db)
        
        # Farm boundary
        farm_boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 10],
                [10, 10],
                [10, 0],
                [0, 0]
            ]]
        }
        
        # Plot boundary (partially outside)
        plot_boundary = {
            "type": "Polygon",
            "coordinates": [[
                [5, 5],
                [5, 15],  # Extends beyond farm
                [15, 15],  # Extends beyond farm
                [15, 5],  # Extends beyond farm
                [5, 5]
            ]]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            service.validate_plot_within_farm(plot_boundary, farm_boundary)
        
        assert exc_info.value.error_code == "PLOT_OUTSIDE_FARM"
    
    def test_plot_same_as_farm(self, db: Session):
        """Test validation succeeds when plot boundary equals farm boundary."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 10],
                [10, 10],
                [10, 0],
                [0, 0]
            ]]
        }
        
        # Same boundary for both
        assert service.validate_plot_within_farm(boundary, boundary) is True


class TestCalculateArea:
    """Test area calculation."""
    
    def test_calculate_area_square(self, db: Session):
        """Test area calculation for a square polygon."""
        service = SpatialService(db)
        
        # Approximately 1 degree x 1 degree square near equator
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1],
                [1, 1],
                [1, 0],
                [0, 0]
            ]]
        }
        
        area = service.calculate_area(boundary)
        
        # Area should be positive
        assert area > 0
        # Area should be a Decimal
        assert isinstance(area, Decimal)
        # Approximate area of 1 degree x 1 degree at equator is ~12,364 km²
        # = ~12,364,000,000 m²
        assert area > 10_000_000_000  # At least 10 billion square meters
    
    def test_calculate_area_small_polygon(self, db: Session):
        """Test area calculation for a small polygon."""
        service = SpatialService(db)
        
        # Small polygon (0.01 x 0.01 degrees)
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 0.01],
                [0.01, 0.01],
                [0.01, 0],
                [0, 0]
            ]]
        }
        
        area = service.calculate_area(boundary)
        
        # Area should be positive but smaller
        assert area > 0
        assert isinstance(area, Decimal)
        # Should be much smaller than the 1x1 degree square
        assert area < 10_000_000_000
    
    def test_calculate_area_invalid_boundary(self, db: Session):
        """Test area calculation fails for invalid boundary."""
        service = SpatialService(db)
        
        # Invalid boundary (not closed)
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1],
                [1, 1],
                [1, 0]  # Not closed
            ]]
        }
        
        with pytest.raises(ValidationError):
            service.calculate_area(boundary)
    
    def test_calculate_area_complex_polygon(self, db: Session):
        """Test area calculation for a more complex polygon."""
        service = SpatialService(db)
        
        # Pentagon-like shape
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1],
                [0.5, 1.5],
                [1, 1],
                [1, 0],
                [0, 0]
            ]]
        }
        
        area = service.calculate_area(boundary)
        
        # Area should be positive
        assert area > 0
        assert isinstance(area, Decimal)


class TestCreatePoint:
    """Test point creation."""
    
    def test_create_point_valid(self, db: Session):
        """Test creating a valid point."""
        service = SpatialService(db)
        
        wkt = service.create_point(45.5, -122.6)
        
        assert wkt == "POINT(-122.6 45.5)"
    
    def test_create_point_invalid_coordinates(self, db: Session):
        """Test creating point with invalid coordinates fails."""
        service = SpatialService(db)
        
        with pytest.raises(ValidationError):
            service.create_point(91, 0)


class TestCreatePolygon:
    """Test polygon creation."""
    
    def test_create_polygon_valid(self, db: Session):
        """Test creating a valid polygon."""
        service = SpatialService(db)
        
        coordinates = [
            [0, 0],
            [0, 1],
            [1, 1],
            [1, 0],
            [0, 0]
        ]
        
        wkt = service.create_polygon(coordinates)
        
        assert wkt == "POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))"
    
    def test_create_polygon_insufficient_points(self, db: Session):
        """Test creating polygon with < 4 points fails."""
        service = SpatialService(db)
        
        coordinates = [
            [0, 0],
            [0, 1],
            [0, 0]
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_polygon(coordinates)
        
        assert exc_info.value.error_code == "INVALID_POLYGON"
    
    def test_create_polygon_not_closed(self, db: Session):
        """Test creating non-closed polygon fails."""
        service = SpatialService(db)
        
        coordinates = [
            [0, 0],
            [0, 1],
            [1, 1],
            [1, 0]
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_polygon(coordinates)
        
        assert exc_info.value.error_code == "POLYGON_NOT_CLOSED"


class TestCalculateDistance:
    """Test distance calculation."""
    
    def test_calculate_distance_same_point(self, db: Session):
        """Test distance between same point is zero."""
        service = SpatialService(db)
        
        point = {"lat": 0, "lon": 0}
        
        distance = service.calculate_distance(point, point)
        
        assert distance == 0
    
    def test_calculate_distance_different_points(self, db: Session):
        """Test distance between different points."""
        service = SpatialService(db)
        
        point1 = {"lat": 0, "lon": 0}
        point2 = {"lat": 0, "lon": 1}
        
        distance = service.calculate_distance(point1, point2)
        
        # Distance should be positive
        assert distance > 0
        # 1 degree longitude at equator is approximately 111 km = 111,000 m
        assert 100_000 < distance < 120_000


class TestCheckIntersection:
    """Test boundary intersection checking."""
    
    def test_check_intersection_overlapping(self, db: Session):
        """Test intersection check for overlapping boundaries."""
        service = SpatialService(db)
        
        boundary1 = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 10],
                [10, 10],
                [10, 0],
                [0, 0]
            ]]
        }
        
        boundary2 = {
            "type": "Polygon",
            "coordinates": [[
                [5, 5],
                [5, 15],
                [15, 15],
                [15, 5],
                [5, 5]
            ]]
        }
        
        assert service.check_intersection(boundary1, boundary2) is True
    
    def test_check_intersection_non_overlapping(self, db: Session):
        """Test intersection check for non-overlapping boundaries."""
        service = SpatialService(db)
        
        boundary1 = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 5],
                [5, 5],
                [5, 0],
                [0, 0]
            ]]
        }
        
        boundary2 = {
            "type": "Polygon",
            "coordinates": [[
                [10, 10],
                [10, 15],
                [15, 15],
                [15, 10],
                [10, 10]
            ]]
        }
        
        assert service.check_intersection(boundary1, boundary2) is False


class TestGetCentroid:
    """Test centroid calculation."""
    
    def test_get_centroid_square(self, db: Session):
        """Test centroid of a square polygon."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 10],
                [10, 10],
                [10, 0],
                [0, 0]
            ]]
        }
        
        centroid = service.get_centroid(boundary)
        
        # Centroid should be at center (5, 5)
        assert "lat" in centroid
        assert "lon" in centroid
        assert abs(centroid["lat"] - 5) < 0.1
        assert abs(centroid["lon"] - 5) < 0.1
    
    def test_get_centroid_returns_dict(self, db: Session):
        """Test centroid returns dict with lat/lon keys."""
        service = SpatialService(db)
        
        boundary = {
            "type": "Polygon",
            "coordinates": [[
                [0, 0],
                [0, 1],
                [1, 1],
                [1, 0],
                [0, 0]
            ]]
        }
        
        centroid = service.get_centroid(boundary)
        
        assert isinstance(centroid, dict)
        assert "lat" in centroid
        assert "lon" in centroid
        assert isinstance(centroid["lat"], float)
        assert isinstance(centroid["lon"], float)
