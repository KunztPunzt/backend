"""agregar tabla auditoria

Revision ID: agregar_tabla_auditoria
Revises: 30241c048b4e
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision = 'agregar_tabla_auditoria'
down_revision = '30241c048b4e'
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla auditoria
    op.create_table(
        'auditoria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tabla', sa.String(length=100), nullable=False),
        sa.Column('accion', sa.String(length=10), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('fecha', sa.DateTime(timezone=True), server_default=sa.text('getdate()'), nullable=False),
        sa.Column('datos_anteriores', mssql.JSON, nullable=True),
        sa.Column('datos_nuevos', mssql.JSON, nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('detalles', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['Usuario.idUser'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índice
    op.create_index(op.f('ix_auditoria_id'), 'auditoria', ['id'], unique=False)

def downgrade():
    # Eliminar índice
    op.drop_index(op.f('ix_auditoria_id'), table_name='auditoria')
    
    # Eliminar tabla
    op.drop_table('auditoria') 