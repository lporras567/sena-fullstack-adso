from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud, schemas
from app.auth import obtener_usuario_actual
from app.models import UsuarioModel

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.get("/", response_model=list[schemas.CursoResponse])
async def listar_cursos(db: AsyncSession = Depends(get_db)):
    return await crud.obtener_cursos(db)


@router.get("/{cid}", response_model=schemas.CursoResponse)
async def buscar_curso(cid: int, db: AsyncSession = Depends(get_db)):
    curso = await crud.obtener_curso_por_id(db, cid)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso


@router.post("/", response_model=schemas.CursoResponse,
             status_code=status.HTTP_201_CREATED)
async def registrar_curso(
    c: schemas.CursoCreate,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    if me.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede crear cursos",
        )
    return await crud.crear_curso(db, c)


@router.post("/{cid}/inscribir/{uid}", response_model=schemas.CursoResponse)
async def inscribir_usuario(
    cid: int,
    uid: int,
    body: schemas.InscripcionBody,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    """
    Inscribe un usuario en un curso.
    Validaciones:
    - fecha_inscripcion <= fecha_inicio del curso
    - inscritos < capacidad
    - el usuario no esté ya inscrito
    """
    return await crud.inscribir_usuario(db, cid, uid, body.fecha_inscripcion)


@router.delete("/{cid}/inscribir/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def desinscribir_usuario(
    cid: int,
    uid: int,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    if not await crud.desinscribir_usuario(db, cid, uid):
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return None


@router.get("/{cid}/usuarios")
async def listar_inscritos(
    cid: int,
    db: AsyncSession = Depends(get_db),
    me: UsuarioModel = Depends(obtener_usuario_actual),
):
    return await crud.obtener_inscritos_con_fecha(db, cid)
