"""Initial schema - Organization-based multi-tenant database

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('google_id', sa.String(255), unique=True, nullable=True, index=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('preferences', sa.JSON(), default=dict),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', sa.JSON(), default=dict),
        sa.Column('plan', sa.String(50), default='free', nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Organization Members table
    op.create_table(
        'organization_members',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(50), default='member', nullable=False),
        sa.Column('status', sa.String(50), default='active', nullable=False),
        sa.Column('invited_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('invited_at', sa.DateTime(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_user'),
    )
    op.create_index('ix_org_member_org_id', 'organization_members', ['organization_id'])
    op.create_index('ix_org_member_user_id', 'organization_members', ['user_id'])

    # Organization Invites table
    op.create_table(
        'organization_invites',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), default='member', nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('invited_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_invite_org_email', 'organization_invites', ['organization_id', 'email'])

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key', sa.String(100), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('team_size', sa.String(50), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('prompt_summary', sa.Text(), nullable=True),
        sa.Column('final_prompt', sa.Text(), nullable=True),
        sa.Column('risk_highlights', sa.JSON(), default=list),
        sa.Column('generated_risks', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), default='draft', nullable=False),
        sa.Column('settings', sa.JSON(), default=dict),
        sa.Column('extra_data', sa.JSON(), default=dict),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('organization_id', 'key', name='uq_org_project_key'),
    )
    op.create_index('ix_project_org_id', 'projects', ['organization_id'])
    op.create_index('ix_project_status', 'projects', ['status'])

    # Features table
    op.create_table(
        'features',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('problem_statement', sa.Text(), nullable=True),
        sa.Column('business_objective', sa.Text(), nullable=True),
        sa.Column('user_persona', sa.Text(), nullable=True),
        sa.Column('acceptance_criteria', sa.Text(), nullable=True),
        sa.Column('detailed_description', sa.Text(), nullable=True),
        sa.Column('success_metrics', sa.Text(), nullable=True),
        sa.Column('dependencies', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), default=0),
        sa.Column('approved', sa.Boolean(), default=False),
        sa.Column('custom_fields', sa.JSON(), default=dict),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_feature_project_id', 'features', ['project_id'])
    op.create_index('ix_feature_order', 'features', ['project_id', 'order_index'])

    # Stories table
    op.create_table(
        'stories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('feature_id', sa.String(36), sa.ForeignKey('features.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('feature_ref', sa.String(255), nullable=True),
        sa.Column('feature_context', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), default=0),
        sa.Column('approved', sa.Boolean(), default=False),
        sa.Column('custom_fields', sa.JSON(), default=dict),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_story_project_id', 'stories', ['project_id'])
    op.create_index('ix_story_feature_id', 'stories', ['feature_id'])
    op.create_index('ix_story_order', 'stories', ['feature_id', 'order_index'])

    # Custom Field Definitions table
    op.create_table(
        'custom_field_definitions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('field_label', sa.String(255), nullable=True),
        sa.Column('field_type', sa.String(50), nullable=False),
        sa.Column('field_options', sa.JSON(), default=list),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('required', sa.Boolean(), default=False),
        sa.Column('order_index', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('organization_id', 'entity_type', 'field_name', name='uq_org_entity_field'),
    )
    op.create_index('ix_custom_field_org', 'custom_field_definitions', ['organization_id'])

    # Designs table
    op.create_table(
        'designs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('design_type', sa.String(50), nullable=False),
        sa.Column('diagram', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('status', sa.String(50), default='pending', nullable=False),
        sa.Column('tokens_used', sa.JSON(), default=dict),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('project_id', 'design_type', name='uq_project_design_type'),
    )
    op.create_index('ix_design_project_id', 'designs', ['project_id'])

    # Wireframe Pages table
    op.create_table(
        'wireframe_pages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_name', sa.String(255), nullable=False),
        sa.Column('page_type', sa.String(100), nullable=True),
        sa.Column('html_content', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), default=0),
        sa.Column('status', sa.String(50), default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_wireframe_page_project_id', 'wireframe_pages', ['project_id'])

    # Wireframe Components table
    op.create_table(
        'wireframe_components',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('component_type', sa.String(50), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('project_id', 'component_type', name='uq_project_component_type'),
    )

    # Generated Apps table
    op.create_table(
        'generated_apps',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('safe_name', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('project_path', sa.Text(), nullable=True),
        sa.Column('frontend_port', sa.Integer(), nullable=True),
        sa.Column('backend_port', sa.Integer(), nullable=True),
        sa.Column('preview_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), default='created', nullable=False),
        sa.Column('docker_compose', sa.Text(), nullable=True),
        sa.Column('frontend_files', sa.JSON(), default=dict),
        sa.Column('backend_files', sa.JSON(), default=dict),
        sa.Column('build_log', sa.Text(), nullable=True),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('stopped_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_generated_app_project_id', 'generated_apps', ['project_id'])
    op.create_index('ix_generated_app_status', 'generated_apps', ['status'])


def downgrade() -> None:
    op.drop_table('generated_apps')
    op.drop_table('wireframe_components')
    op.drop_table('wireframe_pages')
    op.drop_table('designs')
    op.drop_table('custom_field_definitions')
    op.drop_table('stories')
    op.drop_table('features')
    op.drop_table('projects')
    op.drop_table('organization_invites')
    op.drop_table('organization_members')
    op.drop_table('organizations')
    op.drop_table('users')
