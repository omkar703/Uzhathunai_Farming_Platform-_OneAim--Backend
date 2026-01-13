"""
Subscription models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- SubscriptionPlan (lines 77-95)
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import OrganizationType


class SubscriptionPlan(Base):
    """
    Subscription plan model - matches DDL lines 77-95 exactly.
    
    Defines subscription plans with resource limits and pricing.
    """
    
    __tablename__ = "subscription_plans"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Plan information
    name = Column(String(50), nullable=False, unique=True)  # FREE, BASIC, PREMIUM, ENTERPRISE
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(OrganizationType, name='organization_type'))  # FARMING, FSP, or NULL for universal
    
    # Plan details (JSONB)
    resource_limits = Column(JSONB)  # {"crops": 50, "users": 10, "queries": 100}
    features = Column(JSONB)  # Feature flags
    pricing_details = Column(JSONB)  # {"currency": "INR", "billing_cycles": {"monthly": 1000}}
    
    # Ordering and status
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organizations = relationship("Organization", back_populates="subscription_plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name={self.name}, category={self.category})>"
