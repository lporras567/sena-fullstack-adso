from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# ── URL de conexión (hardcodeada para desarrollo local) ──
# En producción (estación 06) esto se mueve al archivo .env
# NUNCA subas este archivo a GitHub si tiene la contraseña real
DATABASE_URL = "postgresql+asyncpg://postgres:tu_contrasena@localhost:5432/sena_mvc_db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
