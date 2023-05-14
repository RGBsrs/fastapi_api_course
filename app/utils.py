from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pwd(password: str) -> str:
    hashed_pwd = pwd_context.hash(password)
    return hashed_pwd
