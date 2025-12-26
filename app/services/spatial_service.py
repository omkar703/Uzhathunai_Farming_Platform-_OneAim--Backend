"""
Spatial service for GIS operations using PostGIS.
"""
from typing import Dict, Any, Tuple, Optional
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import ValidationError

logger = get_logger(__name__)


class SpatialService:
    """Service for spatial/GIS operations using PostGIS."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate latitude and longitude coordinates.
        
        Args:
            lat: Latitude value
            lon: Longitude value
            
        Returns:
            True if coordinates are valid
            
        Raises:
            ValidationError: If coordinates are invalid
        """
        if not (-90 <= lat <= 90):
            raise ValidationError(
                message=f"Invalid latitude: {lat}. Must be between -90 and 90",
                error_code="INVALID_LATITUDE",
                details={"latitude": lat}
            )
        
        if not (-180 <= lon <= 180):
            raise ValidationError(
                message=f"Invalid longitude: {lon}. Must be between -180 and 180",
                error_code="INVALID_LONGITUDE",
                details={"longitude": lon}
            )
        
        logger.info(
            "Coordinates validated",
            extra={"latitude": lat, "longitude": lon}
        )
        
        return True
    
    def create_point(self, lat: float, lon: float) -> str:
        """
        Create a PostGIS POINT geography from coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            WKT string for the point
        """
        self.validate_coordinates(lat, lon)
        return f"POINT({lon} {lat})"
    
    def create_polygon(self, coordinates: list) -> str:
        """
        Create a PostGIS POLYGON geography from coordinates.
        
        Args:
            coordinates: List of [lon, lat] pairs
            
        Returns:
            WKT string for the polygon
            
        Raises:
            ValidationError: If polygon is invalid
        """
        if not coordinates or len(coordinates) < 4:
            raise ValidationError(
                message="Polygon must have at least 4 points",
                error_code="INVALID_POLYGON",
                details={"points_count": len(coordinates) if coordinates else 0}
            )
        
        # Validate each coordinate
        for coord in coordinates:
            if len(coord) != 2:
                raise ValidationError(
                    message="Each coordinate must have exactly 2 values [lon, lat]",
                    error_code="INVALID_COORDINATE_FORMAT",
                    details={"coordinate": coord}
                )
            lon, lat = coord
            self.validate_coordinates(lat, lon)
        
        # Check if polygon is closed (first point == last point)
        if coordinates[0] != coordinates[-1]:
            raise ValidationError(
                message="Polygon must be closed (first point must equal last point)",
                error_code="POLYGON_NOT_CLOSED",
                details={
                    "first_point": coordinates[0],
                    "last_point": coordinates[-1]
                }
            )
        
        # Create WKT string
        points_str = ", ".join([f"{lon} {lat}" for lon, lat in coordinates])
        return f"POLYGON(({points_str}))"
    
    def validate_boundary(self, boundary: Dict[str, Any]) -> bool:
        """
        Validate a GeoJSON boundary polygon.
        
        Args:
            boundary: GeoJSON polygon object
            
        Returns:
            True if boundary is valid
            
        Raises:
            ValidationError: If boundary is invalid
        """
        if not boundary:
            raise ValidationError(
                message="Boundary cannot be empty",
                error_code="EMPTY_BOUNDARY"
            )
        
        if boundary.get('type') != 'Polygon':
            raise ValidationError(
                message="Boundary must be a Polygon",
                error_code="INVALID_BOUNDARY_TYPE",
                details={"type": boundary.get('type')}
            )
        
        coordinates = boundary.get('coordinates', [])
        if not coordinates:
            raise ValidationError(
                message="Boundary coordinates cannot be empty",
                error_code="EMPTY_COORDINATES"
            )
        
        # Validate the outer ring (first element)
        outer_ring = coordinates[0]
        if len(outer_ring) < 4:
            raise ValidationError(
                message="Polygon must have at least 4 points",
                error_code="INSUFFICIENT_POINTS",
                details={"points_count": len(outer_ring)}
            )
        
        # Validate each coordinate
        for coord in outer_ring:
            if len(coord) != 2:
                raise ValidationError(
                    message="Each coordinate must have exactly 2 values [lon, lat]",
                    error_code="INVALID_COORDINATE_FORMAT",
                    details={"coordinate": coord}
                )
            lon, lat = coord
            self.validate_coordinates(lat, lon)
        
        # Check if polygon is closed
        if outer_ring[0] != outer_ring[-1]:
            raise ValidationError(
                message="Polygon must be closed (first point must equal last point)",
                error_code="POLYGON_NOT_CLOSED",
                details={
                    "first_point": outer_ring[0],
                    "last_point": outer_ring[-1]
                }
            )
        
        logger.info(
            "Boundary validated",
            extra={"points_count": len(outer_ring)}
        )
        
        return True
    
    def validate_plot_within_farm(
        self, 
        plot_boundary: Dict[str, Any], 
        farm_boundary: Dict[str, Any]
    ) -> bool:
        """
        Validate that a plot boundary is within a farm boundary.
        
        Args:
            plot_boundary: GeoJSON polygon for plot
            farm_boundary: GeoJSON polygon for farm
            
        Returns:
            True if plot is within farm
            
        Raises:
            ValidationError: If plot is not within farm
        """
        # First validate both boundaries
        self.validate_boundary(plot_boundary)
        self.validate_boundary(farm_boundary)
        
        # Convert to WKT
        plot_coords = plot_boundary['coordinates'][0]
        farm_coords = farm_boundary['coordinates'][0]
        
        plot_wkt = self.create_polygon(plot_coords)
        farm_wkt = self.create_polygon(farm_coords)
        
        # Use PostGIS ST_Within to check containment
        # Note: ST_Within works with geometry, not geography
        # Convert geography to geometry for the check
        query = text("""
            SELECT ST_Within(
                ST_GeogFromText(:plot_wkt)::geometry,
                ST_GeogFromText(:farm_wkt)::geometry
            )
        """)
        
        result = self.db.execute(
            query,
            {"plot_wkt": plot_wkt, "farm_wkt": farm_wkt}
        ).scalar()
        
        if not result:
            raise ValidationError(
                message="Plot boundary must be within farm boundary",
                error_code="PLOT_OUTSIDE_FARM",
                details={
                    "plot_points": len(plot_coords),
                    "farm_points": len(farm_coords)
                }
            )
        
        logger.info(
            "Plot validated within farm",
            extra={
                "plot_points": len(plot_coords),
                "farm_points": len(farm_coords)
            }
        )
        
        return True
    
    def calculate_area(self, boundary: Dict[str, Any]) -> Decimal:
        """
        Calculate the area of a boundary polygon in square meters.
        
        Args:
            boundary: GeoJSON polygon object
            
        Returns:
            Area in square meters
        """
        self.validate_boundary(boundary)
        
        # Convert to WKT
        coords = boundary['coordinates'][0]
        wkt = self.create_polygon(coords)
        
        # Use PostGIS ST_Area to calculate area
        query = text("""
            SELECT ST_Area(ST_GeogFromText(:wkt))
        """)
        
        area_sq_meters = self.db.execute(
            query,
            {"wkt": wkt}
        ).scalar()
        
        logger.info(
            "Area calculated",
            extra={
                "area_sq_meters": float(area_sq_meters),
                "points_count": len(coords)
            }
        )
        
        return Decimal(str(area_sq_meters))
    
    def calculate_distance(
        self, 
        point1: Dict[str, float], 
        point2: Dict[str, float]
    ) -> float:
        """
        Calculate distance between two points in meters.
        
        Args:
            point1: Dict with 'lat' and 'lon' keys
            point2: Dict with 'lat' and 'lon' keys
            
        Returns:
            Distance in meters
        """
        lat1, lon1 = point1['lat'], point1['lon']
        lat2, lon2 = point2['lat'], point2['lon']
        
        self.validate_coordinates(lat1, lon1)
        self.validate_coordinates(lat2, lon2)
        
        wkt1 = self.create_point(lat1, lon1)
        wkt2 = self.create_point(lat2, lon2)
        
        # Use PostGIS ST_Distance
        query = text("""
            SELECT ST_Distance(
                ST_GeogFromText(:wkt1),
                ST_GeogFromText(:wkt2)
            )
        """)
        
        distance = self.db.execute(
            query,
            {"wkt1": wkt1, "wkt2": wkt2}
        ).scalar()
        
        logger.info(
            "Distance calculated",
            extra={
                "point1": point1,
                "point2": point2,
                "distance_meters": float(distance)
            }
        )
        
        return float(distance)
    
    def check_intersection(
        self, 
        boundary1: Dict[str, Any], 
        boundary2: Dict[str, Any]
    ) -> bool:
        """
        Check if two boundaries intersect.
        
        Args:
            boundary1: GeoJSON polygon
            boundary2: GeoJSON polygon
            
        Returns:
            True if boundaries intersect
        """
        self.validate_boundary(boundary1)
        self.validate_boundary(boundary2)
        
        coords1 = boundary1['coordinates'][0]
        coords2 = boundary2['coordinates'][0]
        
        wkt1 = self.create_polygon(coords1)
        wkt2 = self.create_polygon(coords2)
        
        # Use PostGIS ST_Intersects
        query = text("""
            SELECT ST_Intersects(
                ST_GeogFromText(:wkt1),
                ST_GeogFromText(:wkt2)
            )
        """)
        
        result = self.db.execute(
            query,
            {"wkt1": wkt1, "wkt2": wkt2}
        ).scalar()
        
        logger.info(
            "Intersection check",
            extra={
                "intersects": bool(result),
                "boundary1_points": len(coords1),
                "boundary2_points": len(coords2)
            }
        )
        
        return bool(result)
    
    def get_centroid(self, boundary: Dict[str, Any]) -> Dict[str, float]:
        """
        Get the centroid (center point) of a boundary polygon.
        
        Args:
            boundary: GeoJSON polygon
            
        Returns:
            Dict with 'lat' and 'lon' keys
        """
        self.validate_boundary(boundary)
        
        coords = boundary['coordinates'][0]
        wkt = self.create_polygon(coords)
        
        # Use PostGIS ST_Centroid
        query = text("""
            SELECT 
                ST_Y(ST_Centroid(ST_GeogFromText(:wkt))::geometry) as lat,
                ST_X(ST_Centroid(ST_GeogFromText(:wkt))::geometry) as lon
        """)
        
        result = self.db.execute(query, {"wkt": wkt}).fetchone()
        
        centroid = {
            "lat": float(result.lat),
            "lon": float(result.lon)
        }
        
        logger.info(
            "Centroid calculated",
            extra={
                "centroid": centroid,
                "boundary_points": len(coords)
            }
        )
        
        return centroid
