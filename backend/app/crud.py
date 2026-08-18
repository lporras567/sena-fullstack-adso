from datetime import date

from fastapi import HTTPException
from sqlalchemy import insert as sa_insert, select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.models import (
    UsuarioModel,
    DepartamentoModel,
    DireccionModel,
    CursoModel,
    usuario_curso,
)
from app.security import encriptar_password


# ════════════════════════════════════════
#  USUARIOS
# ════════════════════════════════════════

async def obtener_usuarios(db: AsyncSession):
    result = await db.execute(select(UsuarioModel))
    return result.scalars().all()


async def obtener_usuario_por_id(db: AsyncSession, uid: int):
    result = await db.execute(
        select(UsuarioModel).filter(UsuarioModel.id == uid)
    )
    return result.scalars().first()


async def crear_usuario(db: AsyncSession, u: schemas.UsuarioCreate):
    obj = UsuarioModel(
        nombre=u.nombre,
        email=u.email,
        password=encriptar_password(u.password),
        rol=u.rol,
        departamento_id=u.departamento_id,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def actualizar_usuario(db: AsyncSession, uid: int, data: schemas.UsuarioUpdate):
    obj = await obtener_usuario_por_id(db, uid)
    if not obj:
        return None
    campos = data.model_dump(exclude_unset=True)
    if "password" in campos and campos["password"]:
        campos["password"] = encriptar_password(campos["password"])
    for k, v in campos.items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def eliminar_usuario(db: AsyncSession, uid: int) -> bool:
    obj = await obtener_usuario_por_id(db, uid)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


# ════════════════════════════════════════
#  DEPARTAMENTOS
# ════════════════════════════════════════

async def obtener_departamentos(db: AsyncSession):
    result = await db.execute(select(DepartamentoModel))
    return result.scalars().all()


async def obtener_departamento_por_id(db: AsyncSession, did: int):
    result = await db.execute(
        select(DepartamentoModel).filter(DepartamentoModel.id == did)
    )
    return result.scalars().first()


async def crear_departamento(db: AsyncSession, d: schemas.DepartamentoCreate):
    obj = DepartamentoModel(
        nombre=d.nombre,
        codigo=d.codigo,
        direccion_id=d.direccion_id,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def actualizar_departamento(
    db: AsyncSession, did: int, data: schemas.DepartamentoUpdate
):
    obj = await obtener_departamento_por_id(db, did)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def eliminar_departamento(db: AsyncSession, did: int) -> bool:
    obj = await obtener_departamento_por_id(db, did)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


async def obtener_usuarios_de_departamento(db: AsyncSession, did: int):
    result = await db.execute(
        select(DepartamentoModel).filter(DepartamentoModel.id == did)
    )
    depto = result.scalars().first()
    if depto is None:
        return None
    return depto.usuarios  # cargado por lazy="selectin"


# ════════════════════════════════════════
#  DIRECCIONES
# ════════════════════════════════════════

async def obtener_direcciones(db: AsyncSession):
    result = await db.execute(select(DireccionModel))
    return result.scalars().all()


async def crear_direccion(db: AsyncSession, d: schemas.DireccionCreate):
    obj = DireccionModel(nombre=d.nombre)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ════════════════════════════════════════
#  CURSOS
# ════════════════════════════════════════

async def obtener_cursos(db: AsyncSession):
    result = await db.execute(select(CursoModel))
    return result.scalars().all()


async def obtener_curso_por_id(db: AsyncSession, cid: int):
    result = await db.execute(
        select(CursoModel).filter(CursoModel.id == cid)
    )
    return result.scalars().first()


async def crear_curso(db: AsyncSession, c: schemas.CursoCreate):
    obj = CursoModel(**c.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def inscribir_usuario(
    db: AsyncSession,
    curso_id: int,
    usuario_id: int,
    fecha_inscripcion: date,
):
    # 1. Obtener el curso
    curso = await obtener_curso_por_id(db, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    # 2. Validar fecha: inscripción debe ser <= fecha de inicio
    if fecha_inscripcion > curso.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail=(
                f"La fecha de inscripción ({fecha_inscripcion}) debe ser "
                f"menor o igual a la fecha de inicio del curso ({curso.fecha_inicio})"
            ),
        )

    # 3. Validar capacidad
    cnt = (
        await db.execute(
            select(func.count())
            .select_from(usuario_curso)
            .where(usuario_curso.c.curso_id == curso_id)
        )
    ).scalar()
    if cnt >= curso.capacidad:
        raise HTTPException(
            status_code=400,
            detail=f"El curso '{curso.nombre}' ha alcanzado su capacidad máxima ({curso.capacidad})",
        )

    # 4. Validar duplicado
    dup = (
        await db.execute(
            select(usuario_curso)
            .where(usuario_curso.c.usuario_id == usuario_id)
            .where(usuario_curso.c.curso_id == curso_id)
        )
    ).first()
    if dup:
        raise HTTPException(status_code=400, detail="El usuario ya está inscrito en este curso")

    # 5. Insertar
    await db.execute(
        sa_insert(usuario_curso).values(
            usuario_id=usuario_id,
            curso_id=curso_id,
            fecha_inscripcion=fecha_inscripcion,
        )
    )
    await db.commit()

    # Retornar el curso actualizado
    return await obtener_curso_por_id(db, curso_id)


async def desinscribir_usuario(
    db: AsyncSession, curso_id: int, usuario_id: int
) -> bool:
    result = await db.execute(
        sa_delete(usuario_curso)
        .where(usuario_curso.c.curso_id == curso_id)
        .where(usuario_curso.c.usuario_id == usuario_id)
    )
    await db.commit()
    return result.rowcount > 0


async def obtener_inscritos_con_fecha(db: AsyncSession, curso_id: int):
    rows = (
        await db.execute(
            select(usuario_curso).where(usuario_curso.c.curso_id == curso_id)
        )
    ).fetchall()
    return [
        {"usuario_id": r.usuario_id, "fecha_inscripcion": str(r.fecha_inscripcion)}
        for r in rows
    ]
