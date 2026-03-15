from prisma import Prisma
from features.core.jwt_handler import JWTHandler


class AuthService:
    def __init__(self, db: Prisma, jwtHandler: JWTHandler):
        self.db = db
        self.jwtHandler = jwtHandler

    def register(self, username: str, password: str) -> dict:
        return {'success': True}
