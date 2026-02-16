import pytest
from uuid import uuid4
from app.models.enums import ChatContextType
from app.models.chat import ChatChannel

def test_create_channel_existing_null_updated_at(client, auth_headers, db, test_user):
    # Setup: Create a channel with updated_at = None directly in DB
    context_id = str(uuid4())
    channel = ChatChannel(
        context_type=ChatContextType.SUPPORT,
        context_id=context_id,
        name="Corrupted Channel",
        created_by=test_user.id,
        updated_by=test_user.id,
        updated_at=None # Force None
    )
    db.add(channel)
    db.commit()
    
    # Payload matching the existing channel
    payload = {
        "participant_org_id": str(uuid4()), 
        "context_type": ChatContextType.SUPPORT.value,
        "context_id": context_id,
        "name": "Test Support Channel"
    }
    
    # This should find the existing channel and return it.
    # If updated_at is None, response validation should fail with 500.
    response = client.post("/api/v1/chat/channels", json=payload, headers=auth_headers)
    
    # We expect this to FAIL with 500 if the bug exists
    assert response.status_code == 500
