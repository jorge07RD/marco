"""  
Scheduler para enviar recordatorios automáticos de hábitos.
"""
from datetime import datetime
from sqlalchemy import select
import pytz

from app.database import get_db
from app.models import usuario
from app.routers.notifications import send_notification_to_user


async def check_and_send_reminders():
    """
    Función que se ejecuta cada minuto para verificar si hay usuarios
    que deben recibir recordatorios en su hora configurada.
    """
    # Obtener una sesión de base de datos
    async for db in get_db():
        try:
            # Obtener todos los usuarios con recordatorios activos
            result = await db.execute(
                select(usuario).where(
                    usuario.recordatorios_activos,
                    usuario.notificaciones_activas
                )
            )
            users = result.scalars().all()
            
            for user in users:
                try:
                    # Obtener la zona horaria del usuario
                    user_tz = pytz.timezone(user.timezone)
                    
                    # Obtener la hora actual en la zona horaria del usuario
                    now_user_tz = datetime.now(user_tz)
                    current_time = now_user_tz.strftime("%H:%M")
                    
                    # Verificar si coincide con la hora de recordatorio configurada
                    if current_time == user.hora_recordatorio:
                        # Enviar notificación de recordatorio
                        await send_notification_to_user(
                            usuario_id=user.id,
                            title="🎯 ¡Hora de revisar tus hábitos!",
                            body="Es hora de marcar tu progreso del día. ¡Tú puedes!",
                            db=db,
                            tag="daily-reminder"
                        )
                        print(f"Recordatorio enviado a usuario {user.nombre} ({user.id})")
                
                except pytz.exceptions.UnknownTimeZoneError:
                    print(f"Zona horaria inválida para usuario {user.id}: {user.timezone}")
                except Exception as e:
                    print(f"Error procesando recordatorio para usuario {user.id}: {e}")
        
        except Exception as e:
            print(f"Error en check_and_send_reminders: {e}")
        
        finally:
            # Cerrar la sesión
            await db.close()
            break  # Solo necesitamos una iteración del generador
