from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud, schemas
from app.auth import obtener_usuario_actual
from app.models import UsuarioModel

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=list[schemas.UsuarioResponse])
async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    if me.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de Administrador",
        )
    return await crud.obtener_usuarios(db)


@router.get("/{uid}", response_model=schemas.UsuarioResponse)
async def buscar_usuario(
    uid: int,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    usuario = await crud.obtener_usuario_por_id(db, uid)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=schemas.UsuarioResponse,
             status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    u: schemas.UsuarioCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.crear_usuario(db, u)


@router.put("/{uid}", response_model=schemas.UsuarioResponse)
async def modificar_usuario(
    uid: int,
    data: schemas.UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    usuario = await crud.actualizar_usuario(db, uid, data)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_usuario(
    uid: int,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    if me.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede eliminar usuarios",
        )
    if not await crud.eliminar_usuario(db, uid):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return None
