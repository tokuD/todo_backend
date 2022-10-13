from passlib.context import CryptContext



pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(row_password: str, hashed_password: str):
    return pwd_context.verify(row_password, hashed_password)


def hash_password(row_password: str):
    return pwd_context.hash(row_password)