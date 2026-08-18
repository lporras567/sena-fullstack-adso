from __future__ import annotations
from datetime import date
from pydantic import BaseModel, EmailStr


# ── Dirección ──
class DireccionBase(BaseModel):
    nombre: str


class DireccionCreate(DireccionBase):
    pass


class DireccionResponse(DireccionBase):
    id: int

    class Config:
        from_attributes = True


# ── Departamento ──
class DepartamentoBase(BaseModel):
    nombre: str
    codigo: str


class DepartamentoCreate(DepartamentoBase):
    direccion_id: int | None = None


class DepartamentoUpdate(BaseModel):
    nombre:       str | None = None
    codigo:       str | None = None
    direccion_id: int | None = None


class DepartamentoResponse(DepartamentoBase):
    id:           int
    direccion_id: int | None = None
    direccion:    DireccionResponse | None = None

    class Config:
        from_attributes = True


# ── Curso ──
class CursoBase(BaseModel):
    nombre:       str
    descripcion:  str | None = None
    capacidad:    int = 30
    fecha_inicio: date


class CursoCreate(CursoBase):
    pass


class CursoUpdate(BaseModel):
    nombre:       str | None = None
    descripcion:  str | None = None
    capacidad:    int | None = None
    fecha_inicio: date | None = None


class CursoResponse(CursoBase):
    id: int

    class Config:
        from_attributes = True


# ── Usuario ──
class UsuarioBase(BaseModel):
    nombre: str
    email:  EmailStr
    rol:    str = "user"


class UsuarioCreate(UsuarioBase):
    password:       str
    departamento_id: int | None = None


class UsuarioUpdate(BaseModel):
    nombre:          str | None = None
    email:           EmailStr | None = None
    password:        str | None = None
    rol:             str | None = None
    departamento_id: int | None = None


class UsuarioResponse(UsuarioBase):
    id:              int
    departamento_id: int | None = None
    departamento:    DepartamentoResponse | None = None
    cursos:          list[CursoResponse] = []

    class Config:
        from_attributes = True


# ── Inscripción ──
class InscripcionBody(BaseModel):
    fecha_inscripcion: date


# ── Token ──
class Token(BaseModel):
    access_token: str
    token_type:   str
