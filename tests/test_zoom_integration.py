import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from app.services.zoom_service import ZoomService
from app.models.video_session import VideoSession, VideoSessionStatus

@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    return redis

@pytest.fixture
def zoom_service_instance(mock_redis):
    # Patch settings and redis
    with patch("app.services.zoom_service.settings") as mock_settings:
        mock_settings.ZOOM_ACCOUNT_ID = "test_account"
        mock_settings.ZOOM_CLIENT_ID = "test_client"
        mock_settings.ZOOM_CLIENT_SECRET = "test_secret"
        
        service = ZoomService()
        service.redis = mock_redis
        return service

@pytest.mark.asyncio
async def test_get_access_token_uncached(zoom_service_instance):
    """Test getting token when not in cache."""
    # Mock httpx
    with patch("app.services.zoom_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "expires_in": 3600
        }
        mock_client.post.return_value = mock_response
        
        token = await zoom_service_instance.get_access_token()
        
        assert token == "new_token"
        zoom_service_instance.redis.get.assert_called_once()
        zoom_service_instance.redis.set.assert_called_once()

@pytest.mark.asyncio
async def test_get_access_token_cached(zoom_service_instance):
    """Test getting token from cache."""
    zoom_service_instance.redis.get.return_value = "cached_token"
    
    token = await zoom_service_instance.get_access_token()
    
    assert token == "cached_token"
    # Should not make http request if cached
    with patch("app.services.zoom_service.httpx.AsyncClient") as mock_client:
        assert not mock_client.called

@pytest.mark.asyncio
async def test_create_meeting(zoom_service_instance):
    """Test meeting creation logic."""
    zoom_service_instance.get_access_token = AsyncMock(return_value="valid_token")
    
    with patch("app.services.zoom_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123456789,
            "join_url": "https://zoom.us/j/123",
            "start_url": "https://zoom.us/s/123",
            "password": "pass"
        }
        mock_client.post.return_value = mock_response
        
        result = await zoom_service_instance.create_meeting("Test", datetime.now(), 30)
        
        assert result["id"] == 123456789
        assert result["join_url"] == "https://zoom.us/j/123"

# Integration / Background Task Test Logic would typically require full FastAPI TestClient 
# and potentially mocking the DB session or using a test DB. 
# For this unit test file, we focused on the Service Logic isolation as requested.
