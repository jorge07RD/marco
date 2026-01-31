from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.database import init_db
from app.routers import usuarios, categorias, habitos, registros, habito_dias, auth, analisis, notifications

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Log CORS configuration
    logger.info(f"🌐 CORS configurado para: {settings.cors_origins_list}")
    yield
    # Shutdown




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
)

# Routers - Todos bajo el prefijo /api
app.include_router(auth.router, prefix="/api")
app.include_router(usuarios.router, prefix="/api")
app.include_router(categorias.router, prefix="/api")
app.include_router(habitos.router, prefix="/api")
app.include_router(registros.router, prefix="/api")
app.include_router(habito_dias.router, prefix="/api")
app.include_router(analisis.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")


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
