"""
Servicio de notificaciones push.

Utiliza pywebpush para enviar notificaciones push a los navegadores.
"""

import json
import logging
from typing import Optional

from pywebpush import webpush, WebPushException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import push_subscriptions, usuario

logger = logging.getLogger(__name__)
settings = get_settings()


class PushService:
    """Servicio para enviar notificaciones push."""

    def __init__(self):
        self.vapid_private_key = settings.vapid_private_key
        self.vapid_claims = {
            "sub": settings.vapid_claims_email
        }

    def send_notification(
        self,
        subscription_info: dict,
        title: str,
        body: str,
        icon: Optional[str] = None,
        url: Optional[str] = None,
        tag: Optional[str] = None
    ) -> bool:
        """
        Envía una notificación push a una suscripción específica.

        Args:
            subscription_info: Diccionario con endpoint, keys.p256dh, keys.auth
            title: Título de la notificación
            body: Cuerpo de la notificación
            icon: URL del icono (opcional)
            url: URL a abrir al hacer clic (opcional)
            tag: Tag para agrupar notificaciones (opcional)

        Returns:
            True si se envió correctamente, False si falló
        """
        if not self.vapid_private_key:
            logger.error("VAPID private key no configurada")
            return False

        payload = {
            "title": title,
            "body": body,
            "icon": icon or "/favicon.png",
            "badge": "/favicon.png",
            "tag": tag or "marco-notification",
            "data": {
                "url": url or "/"
            }
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            logger.info(f"Notificación enviada: {title}")
            return True
        except WebPushException as e:
            logger.error(f"Error enviando notificación push: {e}")
            # Si el código es 410 (Gone) o 404 (Not Found), la suscripción ya no es válida
            if e.response and e.response.status_code in [404, 410]:
                logger.warning("Suscripción ya no es válida")
            return False
        except Exception as e:
            logger.error(f"Error inesperado enviando notificación: {e}")
            return False

    async def send_to_user(
        self,
        db: AsyncSession,
        user_id: int,
        title: str,
        body: str,
        icon: Optional[str] = None,
        url: Optional[str] = None
    ) -> dict:
        """
        Envía notificación a todas las suscripciones activas de un usuario.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            title: Título de la notificación
            body: Cuerpo de la notificación
            icon: URL del icono (opcional)
            url: URL a abrir al hacer clic (opcional)

        Returns:
            Diccionario con estadísticas: {sent: int, failed: int, invalid: list}
        """
        # Obtener todas las suscripciones activas del usuario
        result = await db.execute(
            select(push_subscriptions).where(
                push_subscriptions.usuario_id == user_id,
                push_subscriptions.activa == True
            )
        )
        subscriptions = result.scalars().all()

        stats = {"sent": 0, "failed": 0, "invalid": []}

        for sub in subscriptions:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh_key,
                    "auth": sub.auth_key
                }
            }

            success = self.send_notification(
                subscription_info=subscription_info,
                title=title,
                body=body,
                icon=icon,
                url=url
            )

            if success:
                stats["sent"] += 1
            else:
                stats["failed"] += 1
                # Marcar suscripción como inactiva si falló
                sub.activa = False
                stats["invalid"].append(sub.id)

        if stats["invalid"]:
            await db.commit()

        return stats


# Instancia global del servicio
push_service = PushService()
