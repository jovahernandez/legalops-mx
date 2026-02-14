"""003 – Pilot readiness: pipeline_stage columns + feedback table.

Revision ID: 003
Revises: 002
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "003"
down_revision = "002"


def upgrade():
    # Add pipeline_stage to intakes
    op.add_column("intakes", sa.Column("pipeline_stage", sa.String(50), server_default="new_intake"))

    # Add pipeline_stage to matters
    op.add_column("matters", sa.Column("pipeline_stage", sa.String(50), server_default="matter_created"))

    # Create feedback table
    op.create_table(
        "feedback",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("anonymous_id", sa.String(100)),
        sa.Column("page", sa.String(255), nullable=False),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("text", sa.Text),
        sa.Column("context_json", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("feedback")
    op.drop_column("matters", "pipeline_stage")
    op.drop_column("intakes", "pipeline_stage")
