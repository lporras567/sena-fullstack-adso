-- ============================================================
-- SENA Backend Empresarial — Script SQL
-- Orden correcto de creación respetando FKs
-- Uso: psql -U sena_user -d sena_mvc_db -f database.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS direcciones (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS departamentos (
    id           SERIAL PRIMARY KEY,
    nombre       VARCHAR(100) UNIQUE NOT NULL,
    codigo       VARCHAR(10)  UNIQUE NOT NULL,
    direccion_id INTEGER REFERENCES direcciones(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    password        VARCHAR(255) NOT NULL,
    rol             VARCHAR(20) DEFAULT 'user' NOT NULL,
    departamento_id INTEGER REFERENCES departamentos(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS cursos (
    id           SERIAL PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    descripcion  TEXT,
    capacidad    INTEGER NOT NULL DEFAULT 30,
    fecha_inicio DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS usuario_curso (
    usuario_id        INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    curso_id          INTEGER REFERENCES cursos(id)   ON DELETE CASCADE,
    fecha_inscripcion DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (usuario_id, curso_id)
);
