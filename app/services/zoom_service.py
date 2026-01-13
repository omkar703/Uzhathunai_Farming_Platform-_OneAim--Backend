"""
Zoom Service for handling OAuth and Meeting Creation.
"""
import httpx
import base64
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException

from app.core.config import settings
from app.core.cache import cache_service

# Zoom API Endpoints
ZOOM_OAUTH_URL = "https://zoom.us/oauth/token"
ZOOM_API_BASE_URL = "https://api.zoom.us/v2"

class ZoomService:
    def __init__(self):
        self.account_id = settings.ZOOM_ACCOUNT_ID
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.redis = cache_service.redis_client

    async def get_access_token(self) -> str:
        """
        Get Zoom Access Token (Server-to-Server OAuth).
        Tries to get from Redis first.
        """
        cache_key = f"{settings.CACHE_PREFIX}:zoom_access_token"
        
        # Try fetch from Redis
        if self.redis:
            cached_token = await self.redis.get(cache_key)
            if cached_token:
                return cached_token

        # Generate fresh token
        auth_string = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        params = {
            "grant_type": "account_credentials",
            "account_id": self.account_id
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(ZOOM_OAUTH_URL, headers=headers, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get Zoom Token: {response.text}")
            
            data = response.json()
            access_token = data["access_token"]
            expires_in = data["expires_in"]
            
            # Cache in Redis (subtract 60s buffer)
            if self.redis:
                await self.redis.set(cache_key, access_token, ex=expires_in - 60)
            
            return access_token

    async def create_meeting(self, topic: str, start_time: datetime, duration: int) -> Dict[str, Any]:
        """
        Create a scheduled meeting on Zoom.
        """
        token = await self.get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "topic": topic,
            "type": 2, # Scheduled meeting
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"), # UTC Format
            "duration": duration,
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": False # Simplifies logic for mvp
            }
        }
        
        # Use 'me' if using Account Credentials creates for the owner of the app, 
        # or use specific userId if managed under same account. 'me' is safe for Server-to-Server 
        # as it maps to the account owner/admin usually.
        url = f"{ZOOM_API_BASE_URL}/users/me/meetings"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 201:
                raise Exception(f"Failed to create Zoom meeting: {response.text}")
                
            return response.json()

zoom_service = ZoomService()
