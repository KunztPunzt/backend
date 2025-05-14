"""add VeterinarioServicio

Revision ID: 7fd44496ef99
Revises: 
Create Date: 2025-05-02 19:34:13.448575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fd44496ef99'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "VeterinarioServicio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "veterinarioId", sa.Integer(),
            sa.ForeignKey("Veterinario.idVeterinario", ondelete="CASCADE"),
            nullable=False
        ),
        sa.Column(
            "servicioId", sa.Integer(),
            sa.ForeignKey("Servicio.idServicio", ondelete="CASCADE"),
            nullable=False
        ),
        sa.Column("precioEspecial", sa.Numeric(10, 2), nullable=True),
        sa.Column("duracionMin", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_VeterinarioServicio_veterinarioId",
        "VeterinarioServicio", ["veterinarioId"], unique=False
    )
    op.create_index(
        "ix_VeterinarioServicio_servicioId",
        "VeterinarioServicio", ["servicioId"], unique=False
    )




def downgrade() -> None:
    op.drop_table("VeterinarioServicio")
