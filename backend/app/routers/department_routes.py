from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud, schemas
from app.auth import obtener_usuario_actual
from app.models import UsuarioModel

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.get("/", response_model=list[schemas.DepartamentoResponse])
async def listar_departamentos(db: AsyncSession = Depends(get_db)):
    return await crud.obtener_departamentos(db)


@router.get("/{did}", response_model=schemas.DepartamentoResponse)
async def buscar_departamento(did: int, db: AsyncSession = Depends(get_db)):
    depto = await crud.obtener_departamento_por_id(db, did)
    if not depto:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return depto


@router.get("/{did}/usuarios", response_model=list[schemas.UsuarioResponse])
async def listar_usuarios_departamento(
    did: int,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    usuarios = await crud.obtener_usuarios_de_departamento(db, did)
    if usuarios is None:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return usuarios


@router.post("/", response_model=schemas.DepartamentoResponse,
             status_code=status.HTTP_201_CREATED)
async def registrar_departamento(
    d: schemas.DepartamentoCreate,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    return await crud.crear_departamento(db, d)


@router.put("/{did}", response_model=schemas.DepartamentoResponse)
async def modificar_departamento(
    did: int,
    data: schemas.DepartamentoUpdate,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    depto = await crud.actualizar_departamento(db, did, data)
    if not depto:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return depto


@router.delete("/{did}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_departamento(
    did: int,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    if me.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede eliminar departamentos",
        )
    if not await crud.eliminar_departamento(db, did):
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return None
