"""
Template models for Farm Audit Management System.

Templates are reusable audit structures composed of sections and parameters.
They support system-level and organization-level configurations with multilingual content.
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from typing import Optional

from app.core.database import Base


class Template(Base):
    """
    Template model - Reusable audit structure for specific crop types.
    
    Templates can be system-defined (available to all) or organization-specific.
    Each template is composed of sections containing parameters.
    """
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    is_system_defined = Column(Boolean, default=True, nullable=False)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    crop_type_id = Column(UUID(as_uuid=True), ForeignKey("crop_types.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    owner_organization = relationship("Organization", foreign_keys=[owner_org_id])
    crop_type = relationship("CropType", foreign_keys=[crop_type_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    translations = relationship("TemplateTranslation", back_populates="template", cascade="all, delete-orphan")
    template_sections = relationship("TemplateSection", back_populates="template", cascade="all, delete-orphan")
    
    @property
    def sections(self):
        """Alias for template_sections to support Pydantic model"""
        return self.template_sections

    @property
    def name(self) -> str:
        """Get name from translations (prefer 'en', fallback to first)."""
        if not self.translations:
            return self.code
        
        # Try to find English translation
        for t in self.translations:
            if t.language_code == 'en':
                return t.name
        
        # Fallback to first available
        return self.translations[0].name

    @property
    def description(self) -> Optional[str]:
        """Get description from translations (prefer 'en', fallback to first)."""
        if not self.translations:
            return None
            
        # Try to find English translation
        for t in self.translations:
            if t.language_code == 'en':
                return t.description
        
        # Fallback to first available
        return self.translations[0].description

    @property
    def owner_org_name(self) -> Optional[str]:
        """Get owner organization name."""
        if self.owner_organization:
            return self.owner_organization.name
        return None

    def __repr__(self):
        return f"<Template(id={self.id}, code={self.code}, version={self.version})>"


class TemplateTranslation(Base):
    """
    Template translation model - Multilingual content for templates.
    
    Supports multiple languages (English, Tamil, Malayalam) for template names and descriptions.
    """
    __tablename__ = "template_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    template = relationship("Template", back_populates="translations")

    # Constraints
    __table_args__ = (
        UniqueConstraint('template_id', 'language_code', name='uq_template_translation_lang'),
    )

    def __repr__(self):
        return f"<TemplateTranslation(template_id={self.template_id}, language={self.language_code})>"


class TemplateSection(Base):
    """
    Template section model - Mapping between templates and sections.
    
    Defines which sections are included in a template and their ordering.
    """
    __tablename__ = "template_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    template = relationship("Template", back_populates="template_sections")
    section = relationship("Section")
    template_parameters = relationship("TemplateParameter", back_populates="template_section", cascade="all, delete-orphan")

    @property
    def parameters(self):
        """Alias for template_parameters to support Pydantic model"""
        return self.template_parameters

    @property
    def section_code(self) -> str:
        """Get section code"""
        return self.section.code if self.section else None

    @property
    def section_name(self) -> str:
        """Get section name (prefer 'en', fallback to first)"""
        if not self.section or not self.section.translations:
            return self.section.code if self.section else None
            
        # Try to find English translation
        for t in self.section.translations:
            if t.language_code == 'en':
                return t.name
        
        # Fallback to first available
        return self.section.translations[0].name

    def __repr__(self):
        return f"<TemplateSection(id={self.id}, template_id={self.template_id}, section_id={self.section_id})>"


class TemplateParameter(Base):
    """
    Template parameter model - Mapping between template sections and parameters.
    
    Defines which parameters are included in each template section, their ordering,
    required status, and captures a snapshot of the parameter configuration.
    """
    __tablename__ = "template_parameters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_sections.id", ondelete="CASCADE"), nullable=False)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey("parameters.id"), nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    parameter_snapshot = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    template_section = relationship("TemplateSection", back_populates="template_parameters")
    parameter = relationship("Parameter")
    
    @property
    def name(self) -> Optional[str]:
        """Get parameter name (prefer 'en', fallback to first)."""
        if not self.parameter or not self.parameter.translations:
            # Fallback to code if no translations
            return self.parameter.code if self.parameter else None
            
        # Try to find English translation
        for t in self.parameter.translations:
            if t.language_code == 'en':
                return t.name
        
        # Fallback to first available
        return self.parameter.translations[0].name

    def __repr__(self):
        return f"<TemplateParameter(id={self.id}, template_section_id={self.template_section_id}, parameter_id={self.parameter_id})>"
