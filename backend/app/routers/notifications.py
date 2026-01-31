"""
Router para gestionar notificaciones push.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Dict
import json

from app.database import get_db
from app.models import push_subscription, usuario
from app.schemas import PushSubscriptionCreate
from app.security import get_current_user
from app.config import get_settings
from pywebpush import webpush, WebPushException

router = APIRouter(tags=["notifications"])
settings = get_settings()


@router.get("/notifications/vapid-public-key", response_model=Dict[str, str])
async def get_vapid_public_key():
    """
    Retorna la clave pública VAPID necesaria para suscribirse a notificaciones push.
    """
    if not settings.vapid_public_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VAPID keys no configuradas. Ejecuta: npx web-push generate-vapid-keys"
        )
    
    return {"publicKey": settings.vapid_public_key}


@router.post("/notifications/subscribe", response_model=Dict[str, str])
async def subscribe_to_push(
    subscription_data: PushSubscriptionCreate,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Guarda una suscripción push para el usuario actual.
    """
    try:
        # Verificar si ya existe una suscripción con este endpoint
        result = await db.execute(
            select(push_subscription).where(push_subscription.endpoint == subscription_data.endpoint)
        )
        existing_subscription = result.scalar_one_or_none()
        
        if existing_subscription:
            # Actualizar el usuario_id si cambió
            if existing_subscription.usuario_id != current_user.id:
                existing_subscription.usuario_id = current_user.id
                await db.commit()
            return {"message": "Suscripción actualizada correctamente"}
        
        # Crear nueva suscripción
        new_subscription = push_subscription(
            usuario_id=current_user.id,
            endpoint=subscription_data.endpoint,
            p256dh_key=subscription_data.keys.get("p256dh", ""),
            auth_key=subscription_data.keys.get("auth", "")
        )
        
        db.add(new_subscription)
        await db.commit()
        
        return {"message": "Suscripción creada correctamente"}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar la suscripción: {str(e)}"
        )


@router.delete("/notifications/unsubscribe", response_model=Dict[str, str])
async def unsubscribe_from_push(
    endpoint: str,
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina una suscripción push del usuario actual.
    """
    try:
        result = await db.execute(
            delete(push_subscription).where(
                push_subscription.endpoint == endpoint,
                push_subscription.usuario_id == current_user.id
            )
        )
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suscripción no encontrada"
            )
        
        return {"message": "Suscripción eliminada correctamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la suscripción: {str(e)}"
        )


@router.post("/notifications/test", response_model=Dict[str, str])
async def send_test_notification(
    current_user: usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Envía una notificación de prueba a todas las suscripciones del usuario actual.
    """
    if not settings.vapid_private_key or not settings.vapid_public_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VAPID keys no configuradas"
        )
    
    # Obtener todas las suscripciones del usuario
    result = await db.execute(
        select(push_subscription).where(push_subscription.usuario_id == current_user.id)
    )
    subscriptions = result.scalars().all()
    
    if not subscriptions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay suscripciones activas para este usuario"
        )
    
    # Preparar el payload de la notificación
    notification_payload = json.dumps({
        "title": "🎯 Notificación de Prueba",
        "body": "¡Tu sistema de notificaciones funciona correctamente!",
        "icon": "/favicon.ico",
        "badge": "/favicon.ico",
        "tag": "test-notification"
    })
    
    sent_count = 0
    failed_endpoints = []
    
    # Enviar notificación a cada suscripción
    for sub in subscriptions:
        try:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh_key,
                    "auth": sub.auth_key
                }
            }
            
            webpush(
                subscription_info=subscription_info,
                data=notification_payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_claims_email}
            )
            sent_count += 1
            
        except WebPushException as e:
            # Si la suscripción expiró (410 Gone), eliminarla
            if e.response and e.response.status_code == 410:
                await db.delete(sub)
                failed_endpoints.append(sub.endpoint)
            else:
                print(f"Error enviando notificación: {e}")
        
        except Exception as e:
            print(f"Error inesperado: {e}")
    
    await db.commit()
    
    message = f"Notificación enviada a {sent_count} dispositivo(s)"
    if failed_endpoints:
        message += f". {len(failed_endpoints)} suscripción(es) expirada(s) eliminada(s)."
    
    return {"message": message}


async def send_notification_to_user(
    usuario_id: int,
    title: str,
    body: str,
    db: AsyncSession,
    tag: str = "reminder"
):
    """
    Función auxiliar para enviar notificaciones a un usuario específico.
    Usada por el scheduler para enviar recordatorios.
    """
    if not settings.vapid_private_key or not settings.vapid_public_key:
        print("VAPID keys no configuradas")
        return
    
    # Obtener todas las suscripciones del usuario
    result = await db.execute(
        select(push_subscription).where(push_subscription.usuario_id == usuario_id)
    )
    subscriptions = result.scalars().all()
    
    if not subscriptions:
        return
    
    # Preparar el payload de la notificación
    notification_payload = json.dumps({
        "title": title,
        "body": body,
        "icon": "/favicon.ico",
        "badge": "/favicon.ico",
        "tag": tag
    })
    
    # Enviar notificación a cada suscripción
    for sub in subscriptions:
        try:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh_key,
                    "auth": sub.auth_key
                }
            }
            
            webpush(
                subscription_info=subscription_info,
                data=notification_payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_claims_email}
            )
            
        except WebPushException as e:
            # Si la suscripción expiró (410 Gone), eliminarla
            if e.response and e.response.status_code == 410:
                await db.delete(sub)
        
        except Exception as e:
            print(f"Error enviando notificación: {e}")
    
    await db.commit()
