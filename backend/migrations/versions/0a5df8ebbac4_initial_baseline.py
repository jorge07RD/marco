"""
Migración inicial - Baseline

Este es el punto de partida para el sistema de migraciones.
La base de datos ya existía antes de configurar Alembic, por lo que
esta migración está vacía y solo marca el estado inicial.

Tablas existentes en este punto:
- usuarios: Usuarios del sistema
- categorias: Categorías de hábitos
- habitos: Hábitos de los usuarios
- registros: Registros diarios por usuario
- progreso_habitos: Progreso de cada hábito en un registro
- habito_dias: Días asociados a hábitos
- registro_habito_dias: Relación entre registros y habito_dias

Revision ID: 0a5df8ebbac4
Revises:
Create Date: 2026-01-31

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '0a5df8ebbac4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Baseline - No hay cambios.

    La base de datos ya existe con el esquema completo.
    Esta migración solo marca el punto de partida.
    """
    pass


def downgrade() -> None:
    """
    Baseline - No hay cambios.
    """
    pass
