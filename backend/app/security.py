from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encriptar_password(password: str) -> str:
    """Genera el hash Bcrypt de la contraseña. Hashear ≠ encriptar: es de una sola vía."""
    return pwd_context.hash(password)


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña plana con el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)
