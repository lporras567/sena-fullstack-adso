"""
Tests asíncronos del backend SENA.
Usa SQLite en memoria cuando TESTING=true (no requiere PostgreSQL).
Ejecutar: pytest tests/ -v
"""
import os
import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("TESTING", "true")

from app.main import app  # noqa: E402


# ── Helper ──────────────────────────────────────────────────
async def get_token(ac: AsyncClient, email: str, password: str) -> str:
    r = await ac.post("/login", data={"username": email, "password": password})
    return r.json().get("access_token", "")


# ── Root ─────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_raiz():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        r = await ac.get("/")
    assert r.status_code == 200
    assert "mensaje" in r.json()


# ── Autenticación ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_login_fallido():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        r = await ac.post("/login", data={
            "username": "noexiste@sena.edu.co",
            "password": "ClaveErronea",
        })
    assert r.status_code == 400
    assert r.json()["detail"] == "Correo o contraseña incorrectos"


# ── Usuarios ─────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_listar_usuarios_sin_token():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        r = await ac.get("/usuarios/")
    assert r.status_code == 401


# ── Cursos: inscripción válida ────────────────────────────────
@pytest.mark.asyncio
async def test_cp_curso_02_capacidad_excedida():
    """CP-CURSO-02: no se puede inscribir si el cupo está lleno."""
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        # Crear usuario admin para el test
        await ac.post("/usuarios/", json={
            "nombre": "Admin Test",
            "email": "admin_test@sena.edu.co",
            "password": "sena2026",
            "rol": "admin",
        })
        token = await get_token(ac, "admin_test@sena.edu.co", "sena2026")
        headers = {"Authorization": f"Bearer {token}"}

        fecha_inicio = str(date.today() + timedelta(days=30))

        # Crear curso con capacidad 1
        cr = await ac.post("/cursos", json={
            "nombre": "Curso Capacidad 1",
            "capacidad": 1,
            "fecha_inicio": fecha_inicio,
        }, headers=headers)
        assert cr.status_code == 201
        cid = cr.json()["id"]

        # Crear dos usuarios para inscribir
        u1 = await ac.post("/usuarios/", json={
            "nombre": "Usuario Uno",
            "email": "u1_test@sena.edu.co",
            "password": "sena2026",
        })
        u2 = await ac.post("/usuarios/", json={
            "nombre": "Usuario Dos",
            "email": "u2_test@sena.edu.co",
            "password": "sena2026",
        })
        uid1 = u1.json()["id"]
        uid2 = u2.json()["id"]
        fecha_insc = str(date.today())

        # Primera inscripción — debe funcionar
        r1 = await ac.post(
            f"/cursos/{cid}/inscribir/{uid1}",
            json={"fecha_inscripcion": fecha_insc},
            headers=headers,
        )
        assert r1.status_code == 200

        # Segunda inscripción — cupo lleno
        r2 = await ac.post(
            f"/cursos/{cid}/inscribir/{uid2}",
            json={"fecha_inscripcion": fecha_insc},
            headers=headers,
        )
        assert r2.status_code == 400
        detail = r2.json()["detail"].lower()
        assert "capacidad" in detail or "cupo" in detail


@pytest.mark.asyncio
async def test_cp_curso_03_fecha_invalida():
    """CP-CURSO-03: fecha de inscripción posterior al inicio → 400."""
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        await ac.post("/usuarios/", json={
            "nombre": "Admin Fecha",
            "email": "admin_fecha@sena.edu.co",
            "password": "sena2026",
            "rol": "admin",
        })
        token = await get_token(ac, "admin_fecha@sena.edu.co", "sena2026")
        headers = {"Authorization": f"Bearer {token}"}

        fecha_inicio = str(date.today() + timedelta(days=5))
        cr = await ac.post("/cursos", json={
            "nombre": "Curso Fecha",
            "capacidad": 10,
            "fecha_inicio": fecha_inicio,
        }, headers=headers)
        cid = cr.json()["id"]

        u = await ac.post("/usuarios/", json={
            "nombre": "Estudiante",
            "email": "est_fecha@sena.edu.co",
            "password": "sena2026",
        })
        uid = u.json()["id"]

        # Fecha posterior al inicio → 400
        fecha_futura = str(date.today() + timedelta(days=10))
        r = await ac.post(
            f"/cursos/{cid}/inscribir/{uid}",
            json={"fecha_inscripcion": fecha_futura},
            headers=headers,
        )
        assert r.status_code == 400
        assert "fecha" in r.json()["detail"].lower()
