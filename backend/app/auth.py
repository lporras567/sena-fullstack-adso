import os
import jwt
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import UsuarioModel

# ── Configuración ──
# En producción estas constantes vienen del .env (ver estación 06)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "clave_local_de_desarrollo_cambiar_en_produccion")
ALGORITHM  = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def crear_token_acceso(data: dict) -> str:
    """Firma el payload con la SECRET_KEY y agrega fecha de expiración."""
    datos = data.copy()
    datos["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)


async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UsuarioModel:
    """Dependencia: valida el JWT y retorna el usuario autenticado."""
    credenciales_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credenciales_exc
    except jwt.PyJWTError:
        raise credenciales_exc

    result = await db.execute(
        select(UsuarioModel).filter(UsuarioModel.email == email)
    )
    usuario = result.scalars().first()
    if not usuario:
        raise credenciales_exc
    return usuario
