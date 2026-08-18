# SENA Fullstack ADSO — Backend Empresarial

Stack completo **FastAPI async + PostgreSQL + Angular 19**
Programa ADSO 228118 · SENA CDMC Itagüí
**Instructor:** Ing. Luis Eladio Porras Camargo

## Inicio rápido sin Docker

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Editar .env con tus credenciales de PostgreSQL
uvicorn app.main:app --reload
# API en http://localhost:8000/docs
```

## Inicio rápido con Docker Desktop

```powershell
copy backend\.env.example backend\.env
# Editar backend\.env con tus credenciales
docker compose up --build -d
# API en http://localhost/docs
```

## Cursos interactivos (docs/)

| Archivo | Contenido |
|---------|-----------|
| Curso_Backend_Empresarial_8est.html | MVC async, JWT, N:M, pytest |
| Frontend_Angular_4Sesiones.html | Angular 19, Signals, Guards |
| Deploy_Backend_4Estaciones.html | Deploy Linux, Nginx, CI/CD |
| Deploy_Windows11_4Estaciones.html | Docker Desktop Windows 11 |
| Deploy_SinDocker_SinNginx_Windows11.html | Uvicorn + PostgreSQL nativo |
