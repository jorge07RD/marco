"""
Agregar soporte para notificaciones push

Esta migración marca el estado del esquema de notificaciones push.
Las tablas y columnas ya existen en la base de datos.

Esquema existente:
- usuarios: notificaciones_activas, recordatorios_activos, hora_recordatorio, timezone
- push_subscriptions: id, usuario_id, endpoint, p256dh_key, auth_key, created_at

Cambios en esta migración:
- Agregar columnas faltantes: user_agent, activa en push_subscriptions

Revision ID: b1c2d3e4f5g6
Revises: 0a5df8ebbac4
Create Date: 2026-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, Sequence[str], None] = '0a5df8ebbac4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar columnas faltantes a push_subscriptions."""
    # Agregar columnas que faltan en push_subscriptions
    try:
        op.add_column('push_subscriptions', sa.Column('user_agent', sa.String(), nullable=True))
    except Exception:
        pass  # La columna ya existe

    try:
        op.add_column('push_subscriptions', sa.Column('activa', sa.Boolean(), nullable=True, server_default='1'))
    except Exception:
        pass  # La columna ya existe


def downgrade() -> None:
    """Eliminar columnas agregadas."""
    try:
        op.drop_column('push_subscriptions', 'activa')
    except Exception:
        pass

    try:
        op.drop_column('push_subscriptions', 'user_agent')
    except Exception:
        pass
