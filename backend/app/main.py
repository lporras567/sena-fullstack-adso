from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import (
    auth_routes,
    user_routes,
    department_routes,
    direction_routes,
    course_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas al arrancar si no existen (equivalente async de create_all)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="SENA Backend Empresarial — MVC Async",
    description=(
        "API REST asíncrona con FastAPI + PostgreSQL + SQLAlchemy async. "
        "Programa ADSO 228118 · SENA CDMC Itagüí."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # en producción especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(department_routes.router)
app.include_router(direction_routes.router)
app.include_router(course_routes.router)


@app.get("/", tags=["Root"])
async def inicio():
    return {"mensaje": "Backend MVC Asíncrono activo — visita /docs para la API"}
