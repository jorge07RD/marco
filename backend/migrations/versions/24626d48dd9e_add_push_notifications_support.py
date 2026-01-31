"""add push notifications support

Revision ID: 24626d48dd9e
Revises: b1c2d3e4f5g6
Create Date: 2026-01-31 10:36:37.581309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24626d48dd9e'
down_revision: Union[str, Sequence[str], None] = '0a5df8ebbac4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar soporte completo para notificaciones push."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # 1. Agregar columnas a la tabla usuarios si no existen
    usuarios_columns = {col['name'] for col in inspector.get_columns('usuarios')}
    
    if 'notificaciones_activas' not in usuarios_columns:
        op.add_column('usuarios', sa.Column('notificaciones_activas', sa.Boolean(), server_default='false'))
    
    if 'recordatorios_activos' not in usuarios_columns:
        op.add_column('usuarios', sa.Column('recordatorios_activos', sa.Boolean(), server_default='false'))
    
    if 'hora_recordatorio' not in usuarios_columns:
        op.add_column('usuarios', sa.Column('hora_recordatorio', sa.String(), server_default="'08:00'"))
    
    if 'timezone' not in usuarios_columns:
        op.add_column('usuarios', sa.Column('timezone', sa.String(), server_default="'America/Mexico_City'"))
    
    # 2. Crear tabla push_subscriptions si no existe
    tables = inspector.get_table_names()
    if 'push_subscriptions' not in tables:
        op.create_table(
            'push_subscriptions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('usuario_id', sa.Integer(), nullable=False),
            sa.Column('endpoint', sa.String(), nullable=False),
            sa.Column('p256dh_key', sa.String(), nullable=False),
            sa.Column('auth_key', sa.String(), nullable=False),
            sa.Column('user_agent', sa.String(), nullable=True),
            sa.Column('activa', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('endpoint')
        )
        op.create_index(op.f('ix_push_subscriptions_id'), 'push_subscriptions', ['id'], unique=False)


def downgrade() -> None:
    """Eliminar soporte de notificaciones push."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Eliminar tabla push_subscriptions si existe
    tables = inspector.get_table_names()
    if 'push_subscriptions' in tables:
        op.drop_index(op.f('ix_push_subscriptions_id'), table_name='push_subscriptions')
        op.drop_table('push_subscriptions')
    
    # Eliminar columnas de usuarios si existen
    usuarios_columns = {col['name'] for col in inspector.get_columns('usuarios')}
    
    if 'timezone' in usuarios_columns:
        op.drop_column('usuarios', 'timezone')
    
    if 'hora_recordatorio' in usuarios_columns:
        op.drop_column('usuarios', 'hora_recordatorio')
    
    if 'recordatorios_activos' in usuarios_columns:
        op.drop_column('usuarios', 'recordatorios_activos')
    
    if 'notificaciones_activas' in usuarios_columns:
        op.drop_column('usuarios', 'notificaciones_activas')
