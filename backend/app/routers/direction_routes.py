from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud, schemas
from app.auth import obtener_usuario_actual
from app.models import UsuarioModel

router = APIRouter(prefix="/direcciones", tags=["Direcciones"])


@router.get("/", response_model=list[schemas.DireccionResponse])
async def listar_direcciones(db: AsyncSession = Depends(get_db)):
    return await crud.obtener_direcciones(db)


@router.post("/", response_model=schemas.DireccionResponse,
             status_code=status.HTTP_201_CREATED)
async def registrar_direccion(
    d: schemas.DireccionCreate,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    if me.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de Administrador",
        )
    return await crud.crear_direccion(db, d)
