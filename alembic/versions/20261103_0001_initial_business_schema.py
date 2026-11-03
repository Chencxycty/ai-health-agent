"""Create the initial business schema.

Revision ID: 20261103_0001
Revises: None
Create Date: 2026-11-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "20261103_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # PostgreSQL must know the vector type before the embedding column is made.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chunk_id", sa.String(length=64), nullable=False),
        sa.Column("document_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(dim=1024), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_document_chunks_chunk_id",
        "document_chunks",
        ["chunk_id"],
        unique=True,
    )
    op.create_index(
        "ix_document_chunks_document_id",
        "document_chunks",
        ["document_id"],
        unique=False,
    )

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_patients_patient_id",
        "patients",
        ["patient_id"],
        unique=True,
    )

    op.create_table(
        "conditions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("display", sa.String(length=300), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.patient_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_conditions_patient_id",
        "conditions",
        ["patient_id"],
        unique=False,
    )

    op.create_table(
        "observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.String(length=64), nullable=False),
        sa.Column("observation_type", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.patient_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_observations_observation_type",
        "observations",
        ["observation_type"],
        unique=False,
    )
    op.create_index(
        "ix_observations_observed_at",
        "observations",
        ["observed_at"],
        unique=False,
    )
    op.create_index(
        "ix_observations_patient_id",
        "observations",
        ["patient_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_observations_patient_id", table_name="observations")
    op.drop_index("ix_observations_observed_at", table_name="observations")
    op.drop_index("ix_observations_observation_type", table_name="observations")
    op.drop_table("observations")

    op.drop_index("ix_conditions_patient_id", table_name="conditions")
    op.drop_table("conditions")

    op.drop_index("ix_patients_patient_id", table_name="patients")
    op.drop_table("patients")

    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_index("ix_document_chunks_chunk_id", table_name="document_chunks")
    op.drop_table("document_chunks")

    # The vector extension can be shared by schemas outside this application.
    # Do not remove it automatically during a downgrade.
