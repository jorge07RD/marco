from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import usuarios, categorias, habitos, registros, habito_dias, auth, analisis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")  # Auth router sin protección
app.include_router(usuarios.router, prefix="/api")
app.include_router(categorias.router, prefix="/api")
app.include_router(habitos.router, prefix="/api")
app.include_router(registros.router, prefix="/api")
app.include_router(habito_dias.router, prefix="/api")
app.include_router(analisis.router, prefix="/api")


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
