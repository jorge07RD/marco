from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import traceback

from app.config import get_settings
from app.database import init_db
from app.routers import usuarios, categorias, habitos, registros, habito_dias, auth, analisis
# from app.routers import notifications  # Router no existe aún

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("🚀 Iniciando aplicación...")
        logger.info(f"🌍 Entorno: {settings.environment}")
        logger.info(f"🗄️  Database URL: {settings.database_url[:50]}...")
        await init_db()
        logger.info("✅ Base de datos inicializada correctamente")
        logger.info(f"🌐 CORS configurado para: {settings.cors_origins_list}")
    except Exception as e:
        logger.error(f"❌ Error al inicializar la aplicación: {str(e)}")
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        # No lanzar la excepción para que la app siga corriendo
    yield
    # Shutdown
    logger.info("👋 Cerrando aplicación...")




app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS middleware para permitir requests del frontend
# Los orígenes permitidos se configuran en .env (CORS_ORIGINS)
logger.info(f"📋 Variable CORS_ORIGINS raw: {settings.cors_origins}")
logger.info(f"🌐 CORS origins parsed: {settings.cors_origins_list}")

# En producción, permitir todos los orígenes temporalmente para debugging
# IMPORTANTE: ["*"] no funciona con credentials, así que usamos regex
if settings.is_production:
    # Permitir cualquier origen en producción temporalmente
    cors_origins = ["*"]
    allow_credentials = False  # No se puede usar con wildcard
    logger.warning("⚠️  CORS en modo permisivo (solo para debugging)")
else:
    cors_origins = settings.cors_origins_list
    allow_credentials = True

logger.info(f"🔓 CORS origins efectivos: {cors_origins}")
logger.info(f"🔐 Allow credentials: {allow_credentials}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Handler explícito para OPTIONS (preflight CORS)
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    """Maneja requests OPTIONS para CORS preflight."""
    origin = request.headers.get("origin", "*")
    logger.info(f"🔧 OPTIONS request desde: {origin} para: /{rest_of_path}")
    
    response = JSONResponse(content={"status": "ok"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response


# Manejador global de excepciones para agregar headers CORS incluso en errores
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Maneja todas las excepciones no capturadas y agrega headers CORS."""
    logger.error(f"❌ Error no manejado: {str(exc)}")
    logger.error(f"📍 Path: {request.url.path}")
    logger.error(f"🔍 Method: {request.method}")
    logger.error(f"🌍 Headers: {dict(request.headers)}")
    logger.error(f"📋 Traceback: {traceback.format_exc()}")
    
    # Crear respuesta de error
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url.path)
        }
    )
    
    # Agregar headers CORS manualmente (modo permisivo total)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response


# Routers - Todos bajo el prefijo /api
app.include_router(auth.router, prefix="/api")
app.include_router(usuarios.router, prefix="/api")
app.include_router(categorias.router, prefix="/api")
app.include_router(habitos.router, prefix="/api")
app.include_router(registros.router, prefix="/api")
app.include_router(habito_dias.router, prefix="/api")
app.include_router(analisis.router, prefix="/api")
# app.include_router(notifications.router, prefix="/api")  # Router no existe aún


@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "app": settings.app_name,
        "version": settings.api_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint para verificar que la API está funcionando."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.api_version,
        "environment": settings.environment
    }


@app.get("/debug/cors")
async def debug_cors():
    """Endpoint de debug para verificar configuración CORS."""
    return {
        "cors_origins_raw": settings.cors_origins,
        "cors_origins_list": settings.cors_origins_list,
        "environment": settings.environment
    }
