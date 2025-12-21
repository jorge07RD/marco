"""
Utilidades compartidas para la aplicación.

Funciones helper para manejo de días de hábitos, parsing seguro, etc.
"""

import json
import logging
from datetime import date
from typing import List

logger = logging.getLogger(__name__)


def parsear_dias_habito(dias_str: str) -> List[str]:
    """
    Parsea la cadena JSON de días del hábito de forma segura.

    Args:
        dias_str: String JSON con días (ej: '["L", "M", "X"]')

    Returns:
        Lista de días parseada

    Raises:
        ValueError: Si el JSON es inválido o no es una lista de strings
    """
    try:
        dias = json.loads(dias_str)

        # Validar que sea una lista
        if not isinstance(dias, list):
            raise ValueError(f"Esperaba lista de días, recibí {type(dias).__name__}")

        # Validar que todos sean strings
        if not all(isinstance(d, str) for d in dias):
            raise ValueError("Todos los días deben ser strings")

        return dias

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido en dias_habito: {e}") from e


def obtener_dia_letra(fecha: date) -> str:
    """
    Retorna la letra del día de la semana para una fecha.

    Args:
        fecha: Fecha a convertir

    Returns:
        Letra del día: 'L' (Lunes), 'M' (Martes), 'X' (Miércoles),
        'J' (Jueves), 'V' (Viernes), 'S' (Sábado), 'D' (Domingo)

    Note:
        weekday() retorna: 0=Lunes, 1=Martes, ..., 6=Domingo
    """
    dias_semana = {
        0: 'L',  # Lunes
        1: 'M',  # Martes
        2: 'X',  # Miércoles (X para evitar confusión con Martes)
        3: 'J',  # Jueves
        4: 'V',  # Viernes
        5: 'S',  # Sábado
        6: 'D',  # Domingo
    }
    return dias_semana[fecha.weekday()]


def dia_en_lista(dias_str: str, dia_letra: str) -> bool:
    """
    Verifica si un día está en la lista de días del hábito.

    Args:
        dias_str: String JSON con días (ej: '["L", "M", "X"]')
        dia_letra: Letra del día a verificar

    Returns:
        True si el día está en la lista, False si no está o hay error

    Note:
        Si el JSON es inválido, retorna False y loggea el error
    """
    try:
        dias = parsear_dias_habito(dias_str)
        return dia_letra in dias

    except ValueError as e:
        logger.warning(f"Error parseando días del hábito: {e}. dias_str='{dias_str}'")
        return False
