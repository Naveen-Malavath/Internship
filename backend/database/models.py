"""
SQLAlchemy ORM Models for AutoAgents Multi-Tenant Platform.

Schema supports:
- Multi-tenant organizations
- User authentication (Google OAuth)
- Projects with features, stories, designs
- Dynamic custom fields via JSON columns
- Wireframes and generated applications
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    DateTime, ForeignKey, Enum, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
import enum

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string for primary keys."""
    return str(uuid.uuid4())


# ============================================================================
# ENUMS
# ============================================================================

class OrgRole(str, enum.Enum):
    """Organization member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class MemberStatus(str, enum.Enum):
    """Organization member status."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class OrgPlan(str, enum.Enum):
    """Organization subscription plans."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ProjectStatus(str, enum.Enum):
    """Project lifecycle status."""
    DRAFT = "draft"
    ACTIVE = "active"
    GENERATING = "generating"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DesignType(str, enum.Enum):
    """Types of design diagrams."""
    HLD = "hld"
    DBD = "dbd"
    API = "api"
    LLD = "lld"
    DFD = "dfd"
    COMPONENT = "component"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    STATE = "state"
    JOURNEY = "journey"
    SEQUENCE = "sequence"
    MINDMAP = "mindmap"
    GANTT = "gantt"
    GITFLOW = "gitflow"


class DesignStatus(str, enum.Enum):
    """Design generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


class EntityType(str, enum.Enum):
    """Entity types for custom fields."""
    FEATURE = "feature"
    STORY = "story"


class FieldType(str, enum.Enum):
    """Custom field data types."""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    DATE = "date"


class AppStatus(str, enum.Enum):
    """Generated application status."""
    CREATED = "created"
    BUILDING = "building"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class WireframeComponentType(str, enum.Enum):
    """Types of shared wireframe components."""
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    PAGE_WRAPPER = "page_wrapper"


# ============================================================================
# USER & AUTHENTICATION
# ============================================================================

class User(Base):
    """
    User accounts - linked to Google OAuth.
    Users can belong to multiple organizations.
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    preferences = Column(JSON, default=dict)  # User preferences (theme, etc.)
    
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization_memberships = relationship(
        "OrganizationMember", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    created_organizations = relationship(
        "Organization",
        back_populates="creator",
        foreign_keys="Organization.created_by"
    )
    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by"
    )

    def __repr__(self):
        return f"<User {self.email}>"


# ============================================================================
# ORGANIZATIONS (MULTI-TENANCY)
# ============================================================================

class Organization(Base):
    """
    Organizations are the top-level tenant container.
    All projects belong to an organization.
    """
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    logo_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # Organization settings
    settings = Column(JSON, default=dict)
    # Example settings:
    # {
    #     "default_industry": "fintech",
    #     "allowed_domains": ["company.com"],
    #     "features_limit": 100,
    #     "projects_limit": 50
    # }
    
    plan = Column(Enum(OrgPlan), default=OrgPlan.FREE, nullable=False)
    
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="created_organizations", foreign_keys=[created_by])
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    invites = relationship("OrganizationInvite", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    custom_field_definitions = relationship("CustomFieldDefinition", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name}>"


class OrganizationMember(Base):
    """
    Tracks which users belong to which organizations and their roles.
    """
    __tablename__ = "organization_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(Enum(OrgRole), default=OrgRole.MEMBER, nullable=False)
    status = Column(Enum(MemberStatus), default=MemberStatus.ACTIVE, nullable=False)
    
    invited_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    invited_at = Column(DateTime, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    __table_args__ = (
        UniqueConstraint('organization_id', 'user_id', name='uq_org_user'),
        Index('ix_org_member_org_id', 'organization_id'),
        Index('ix_org_member_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<OrganizationMember {self.user_id} in {self.organization_id}>"


class OrganizationInvite(Base):
    """
    Pending invitations to join an organization.
    """
    __tablename__ = "organization_invites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(Enum(OrgRole), default=OrgRole.MEMBER, nullable=False)
    
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    invited_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="invites")
    inviter = relationship("User", foreign_keys=[invited_by])

    __table_args__ = (
        Index('ix_invite_org_email', 'organization_id', 'email'),
    )

    def __repr__(self):
        return f"<OrganizationInvite {self.email} to {self.organization_id}>"


# ============================================================================
# PROJECTS
# ============================================================================

class Project(Base):
    """
    Projects belong to organizations and contain features, stories, designs, etc.
    """
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    key = Column(String(100), nullable=True)  # URL-safe identifier
    industry = Column(String(100), nullable=True)
    team_size = Column(String(50), nullable=True)
    
    # Content fields
    executive_summary = Column(Text, nullable=True)
    prompt_summary = Column(Text, nullable=True)
    final_prompt = Column(Text, nullable=True)
    
    # Risks
    risk_highlights = Column(JSON, default=list)  # Array of strings
    generated_risks = Column(Text, nullable=True)
    
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    
    # Flexible settings and extra data
    settings = Column(JSON, default=dict)
    # Example settings:
    # {
    #     "workflow": {"enableStories": true, "enableWireframes": true},
    #     "stories": {"perFeature": 3}
    # }
    extra_data = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    creator = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    features = relationship("Feature", back_populates="project", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="project", cascade="all, delete-orphan")
    designs = relationship("Design", back_populates="project", cascade="all, delete-orphan")
    wireframe_pages = relationship("WireframePage", back_populates="project", cascade="all, delete-orphan")
    wireframe_components = relationship("WireframeComponent", back_populates="project", cascade="all, delete-orphan")
    generated_apps = relationship("GeneratedApp", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('organization_id', 'key', name='uq_org_project_key'),
        Index('ix_project_org_id', 'organization_id'),
        Index('ix_project_status', 'status'),
    )

    def __repr__(self):
        return f"<Project {self.name}>"


# ============================================================================
# FEATURES & STORIES (with dynamic fields)
# ============================================================================

class Feature(Base):
    """
    Features within a project.
    Supports dynamic custom fields via JSON column.
    """
    __tablename__ = "features"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Core fields (always present)
    title = Column(String(500), nullable=False)
    reason = Column(Text, nullable=True)
    problem_statement = Column(Text, nullable=True)
    business_objective = Column(Text, nullable=True)
    user_persona = Column(Text, nullable=True)
    acceptance_criteria = Column(Text, nullable=True)
    detailed_description = Column(Text, nullable=True)
    success_metrics = Column(Text, nullable=True)
    dependencies = Column(Text, nullable=True)
    
    order_index = Column(Integer, default=0)
    approved = Column(Boolean, default=False)
    
    # Dynamic custom fields defined by users
    custom_fields = Column(JSON, default=dict)
    # Example:
    # {
    #     "priority": "high",
    #     "estimated_hours": 40,
    #     "sprint": "Sprint 3"
    # }
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="features")
    stories = relationship("Story", back_populates="feature", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_feature_project_id', 'project_id'),
        Index('ix_feature_order', 'project_id', 'order_index'),
    )

    def __repr__(self):
        return f"<Feature {self.title}>"


class Story(Base):
    """
    User stories within features.
    Supports dynamic custom fields via JSON column.
    """
    __tablename__ = "stories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    feature_id = Column(String(36), ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    
    # Core fields
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    feature_ref = Column(String(255), nullable=True)
    feature_context = Column(Text, nullable=True)
    
    order_index = Column(Integer, default=0)
    approved = Column(Boolean, default=False)
    
    # Dynamic custom fields
    custom_fields = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="stories")
    feature = relationship("Feature", back_populates="stories")

    __table_args__ = (
        Index('ix_story_project_id', 'project_id'),
        Index('ix_story_feature_id', 'feature_id'),
        Index('ix_story_order', 'feature_id', 'order_index'),
    )

    def __repr__(self):
        return f"<Story {self.title}>"


class CustomFieldDefinition(Base):
    """
    Defines custom fields that users can add to features or stories.
    Organization-level so all projects in org share field definitions.
    """
    __tablename__ = "custom_field_definitions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    entity_type = Column(Enum(EntityType), nullable=False)  # feature or story
    field_name = Column(String(100), nullable=False)
    field_label = Column(String(255), nullable=True)
    field_type = Column(Enum(FieldType), nullable=False)
    field_options = Column(JSON, default=list)  # For select: ["low", "medium", "high"]
    default_value = Column(Text, nullable=True)
    required = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="custom_field_definitions")

    __table_args__ = (
        UniqueConstraint('organization_id', 'entity_type', 'field_name', name='uq_org_entity_field'),
        Index('ix_custom_field_org', 'organization_id'),
    )

    def __repr__(self):
        return f"<CustomFieldDefinition {self.field_name}>"


# ============================================================================
# DESIGNS
# ============================================================================

class Design(Base):
    """
    Design diagrams for a project (HLD, DBD, API, etc.).
    Stores Mermaid diagram content and AI-generated summaries.
    """
    __tablename__ = "designs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    design_type = Column(Enum(DesignType), nullable=False)
    diagram = Column(Text, nullable=True)  # Mermaid diagram content
    summary = Column(Text, nullable=True)  # AI-generated summary
    
    version = Column(Integer, default=1)
    status = Column(Enum(DesignStatus), default=DesignStatus.PENDING, nullable=False)
    
    tokens_used = Column(JSON, default=dict)  # {"input": 100, "output": 500}
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="designs")

    __table_args__ = (
        UniqueConstraint('project_id', 'design_type', name='uq_project_design_type'),
        Index('ix_design_project_id', 'project_id'),
    )

    def __repr__(self):
        return f"<Design {self.design_type.value} for {self.project_id}>"


# ============================================================================
# WIREFRAMES
# ============================================================================

class WireframePage(Base):
    """
    Individual wireframe pages for a project.
    Stores full HTML/CSS content.
    """
    __tablename__ = "wireframe_pages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    page_name = Column(String(255), nullable=False)
    page_type = Column(String(100), nullable=True)  # dashboard, list, form, detail
    html_content = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    order_index = Column(Integer, default=0)
    status = Column(Enum(DesignStatus), default=DesignStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="wireframe_pages")

    __table_args__ = (
        Index('ix_wireframe_page_project_id', 'project_id'),
    )

    def __repr__(self):
        return f"<WireframePage {self.page_name}>"


class WireframeComponent(Base):
    """
    Shared wireframe components (sidebar, header, footer).
    """
    __tablename__ = "wireframe_components"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    component_type = Column(Enum(WireframeComponentType), nullable=False)
    html_content = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="wireframe_components")

    __table_args__ = (
        UniqueConstraint('project_id', 'component_type', name='uq_project_component_type'),
    )

    def __repr__(self):
        return f"<WireframeComponent {self.component_type.value}>"


# ============================================================================
# GENERATED APPLICATIONS
# ============================================================================

class GeneratedApp(Base):
    """
    Tracks generated applications and their deployment status.
    Actual code files remain on filesystem; this stores metadata.
    """
    __tablename__ = "generated_apps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    safe_name = Column(String(255), unique=True, nullable=False, index=True)
    project_path = Column(Text, nullable=True)
    
    frontend_port = Column(Integer, nullable=True)
    backend_port = Column(Integer, nullable=True)
    preview_url = Column(Text, nullable=True)
    
    status = Column(Enum(AppStatus), default=AppStatus.CREATED, nullable=False)
    
    docker_compose = Column(Text, nullable=True)
    frontend_files = Column(JSON, default=dict)  # File listing
    backend_files = Column(JSON, default=dict)
    
    build_log = Column(Text, nullable=True)
    error_log = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="generated_apps")

    __table_args__ = (
        Index('ix_generated_app_project_id', 'project_id'),
        Index('ix_generated_app_status', 'status'),
    )

    def __repr__(self):
        return f"<GeneratedApp {self.safe_name}>"
