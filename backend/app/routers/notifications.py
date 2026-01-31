"""
Router de notificaciones push.

Endpoints para gestionar suscripciones push y preferencias de notificación.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import usuario, push_subscriptions
from app.schemas import (
    PushSubscriptionCreate,
    PushSubscriptionResponse,
    NotificationPreferencesUpdate,
    NotificationPreferencesResponse,
    TestNotificationRequest,
    VapidPublicKeyResponse
)
from app.security import get_current_user
from app.config import get_settings
from app.services.push_service import push_service

settings = get_settings()
router = APIRouter(prefix="/notifications", tags=["notificaciones"])


@router.get(
    "/vapid-public-key",
    response_model=VapidPublicKeyResponse,
    summary="Obtener clave pública VAPID",
    description="Retorna la clave pública VAPID necesaria para suscribirse a notificaciones push."
)
async def get_vapid_public_key() -> VapidPublicKeyResponse:
    """Obtiene la clave pública VAPID para el cliente."""
    if not settings.vapid_public_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notificaciones push no configuradas"
        )
    return VapidPublicKeyResponse(public_key=settings.vapid_public_key)


@router.post(
    "/subscribe",
    response_model=PushSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar suscripción push",
    description="Registra una nueva suscripción push para el usuario autenticado."
)
async def subscribe(
    subscription: PushSubscriptionCreate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PushSubscriptionResponse:
    """Registra una suscripción push para recibir notificaciones."""
    # Verificar si ya existe una suscripción con este endpoint
    result = await db.execute(
        select(push_subscriptions).where(
            push_subscriptions.endpoint == subscription.endpoint
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Si existe pero es de otro usuario, actualizar
        if existing.usuario_id != current_user.id:
            existing.usuario_id = current_user.id
            existing.p256dh_key = subscription.p256dh_key
            existing.auth_key = subscription.auth_key
            existing.user_agent = subscription.user_agent
            existing.activa = True
            await db.commit()
            await db.refresh(existing)
            return existing
        # Si ya existe para este usuario, reactivar y actualizar keys
        existing.p256dh_key = subscription.p256dh_key
        existing.auth_key = subscription.auth_key
        existing.user_agent = subscription.user_agent
        existing.activa = True
        await db.commit()
        await db.refresh(existing)
        return existing

    # Crear nueva suscripción
    new_subscription = push_subscriptions(
        usuario_id=current_user.id,
        endpoint=subscription.endpoint,
        p256dh_key=subscription.p256dh_key,
        auth_key=subscription.auth_key,
        user_agent=subscription.user_agent,
        activa=True
    )

    db.add(new_subscription)
    await db.commit()
    await db.refresh(new_subscription)

    # Activar notificaciones para el usuario si no estaban activas
    if not current_user.notificaciones_activas:
        current_user.notificaciones_activas = True
        await db.commit()

    return new_subscription


@router.delete(
    "/unsubscribe",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar suscripción push",
    description="Cancela una suscripción push del usuario autenticado."
)
async def unsubscribe(
    endpoint: str,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancela una suscripción push específica."""
    result = await db.execute(
        select(push_subscriptions).where(
            push_subscriptions.endpoint == endpoint,
            push_subscriptions.usuario_id == current_user.id
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscripción no encontrada"
        )

    await db.delete(subscription)
    await db.commit()

    # Verificar si el usuario tiene otras suscripciones activas
    result = await db.execute(
        select(push_subscriptions).where(
            push_subscriptions.usuario_id == current_user.id,
            push_subscriptions.activa == True
        )
    )
    remaining = result.scalars().all()

    # Si no quedan suscripciones, desactivar notificaciones
    if not remaining:
        current_user.notificaciones_activas = False
        await db.commit()


@router.get(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    summary="Obtener preferencias de notificación",
    description="Retorna las preferencias de notificación del usuario autenticado."
)
async def get_preferences(
    current_user: usuario = Depends(get_current_user)
) -> NotificationPreferencesResponse:
    """Obtiene las preferencias de notificación del usuario."""
    return NotificationPreferencesResponse(
        notificaciones_activas=current_user.notificaciones_activas or False,
        hora_recordatorio=current_user.hora_recordatorio or "08:00",
        timezone=current_user.timezone or "America/Santo_Domingo"
    )


@router.put(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    summary="Actualizar preferencias de notificación",
    description="Actualiza las preferencias de notificación del usuario autenticado."
)
async def update_preferences(
    preferences: NotificationPreferencesUpdate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NotificationPreferencesResponse:
    """Actualiza las preferencias de notificación del usuario."""
    update_data = preferences.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)

    return NotificationPreferencesResponse(
        notificaciones_activas=current_user.notificaciones_activas or False,
        hora_recordatorio=current_user.hora_recordatorio or "08:00",
        timezone=current_user.timezone or "America/Santo_Domingo"
    )


@router.post(
    "/test",
    summary="Enviar notificación de prueba",
    description="Envía una notificación de prueba al usuario autenticado."
)
async def send_test_notification(
    request: TestNotificationRequest,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Envía una notificación de prueba al usuario."""
    # Verificar que el usuario tiene suscripciones activas
    result = await db.execute(
        select(push_subscriptions).where(
            push_subscriptions.usuario_id == current_user.id,
            push_subscriptions.activa == True
        )
    )
    subscriptions = result.scalars().all()

    if not subscriptions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay suscripciones activas. Activa las notificaciones primero."
        )

    # Enviar notificación
    stats = await push_service.send_to_user(
        db=db,
        user_id=current_user.id,
        title=request.title or "Prueba de notificación",
        body=request.body or "¡Las notificaciones funcionan correctamente!",
        url="/"
    )

    if stats["sent"] == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo enviar la notificación. Verifica la configuración."
        )

    return {
        "message": "Notificación enviada",
        "sent": stats["sent"],
        "failed": stats["failed"]
    }
