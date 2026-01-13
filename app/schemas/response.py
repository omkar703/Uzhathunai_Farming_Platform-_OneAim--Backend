from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    """
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable message")
    data: Optional[T] = Field(None, description="Response payload")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
