from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Table
from sqlalchemy.orm import relationship
from app.database import Base

# ── Tabla asociativa N:M Usuarios ↔ Cursos ──
usuario_curso = Table(
    "usuario_curso",
    Base.metadata,
    Column(
        "usuario_id",
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "curso_id",
        Integer,
        ForeignKey("cursos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("fecha_inscripcion", Date, nullable=False),
)


class DireccionModel(Base):
    __tablename__ = "direcciones"

    id     = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)

    departamentos = relationship(
        "DepartamentoModel",
        back_populates="direccion",
        lazy="selectin",
    )


class DepartamentoModel(Base):
    __tablename__ = "departamentos"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    nombre       = Column(String, unique=True, nullable=False)
    codigo       = Column(String, unique=True, nullable=False)
    direccion_id = Column(Integer, ForeignKey("direcciones.id"), nullable=True)

    direccion = relationship(
        "DireccionModel",
        back_populates="departamentos",
        lazy="selectin",
    )
    usuarios = relationship(
        "UsuarioModel",
        back_populates="departamento",
        lazy="selectin",
    )


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    nombre          = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    password        = Column(String, nullable=False)
    rol             = Column(String, default="user", nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True)

    departamento = relationship(
        "DepartamentoModel",
        back_populates="usuarios",
        lazy="selectin",
    )
    cursos = relationship(
        "CursoModel",
        secondary=usuario_curso,
        back_populates="inscritos",
        lazy="selectin",
    )


class CursoModel(Base):
    __tablename__ = "cursos"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    nombre       = Column(String, nullable=False)
    descripcion  = Column(Text, nullable=True)
    capacidad    = Column(Integer, nullable=False, default=30)
    fecha_inicio = Column(Date, nullable=False)

    inscritos = relationship(
        "UsuarioModel",
        secondary=usuario_curso,
        back_populates="cursos",
        lazy="selectin",
    )
