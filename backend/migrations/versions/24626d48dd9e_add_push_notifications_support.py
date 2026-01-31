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
    """Upgrade schema."""
    # Intentar eliminar el índice solo si existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Verificar si la tabla existe
    tables = inspector.get_table_names()
    if 'push_subscriptions' in tables:
        # Obtener índices existentes
        indexes = inspector.get_indexes('push_subscriptions')
        index_names = [idx['name'] for idx in indexes]
        
        # Solo eliminar el índice si existe
        if 'idx_push_subscriptions_usuario_id' in index_names:
            op.drop_index('idx_push_subscriptions_usuario_id', table_name='push_subscriptions')


def downgrade() -> None:
    """Downgrade schema."""
    # Recrear el índice solo si no existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    tables = inspector.get_table_names()
    if 'push_subscriptions' in tables:
        indexes = inspector.get_indexes('push_subscriptions')
        index_names = [idx['name'] for idx in indexes]
        
        if 'idx_push_subscriptions_usuario_id' not in index_names:
            op.create_index('idx_push_subscriptions_usuario_id', 'push_subscriptions', ['usuario_id'], unique=False)
