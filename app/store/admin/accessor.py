import typing
from hashlib import sha256
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        # TODO: создать админа по данным в config.yml здесь
        await self.create_admin(self.app.config.admin.email,
                                self.app.config.admin.password)

    async def get_by_email(self, email: str) -> Optional[Admin]:
        admins = self.app.database.admins
        for admin in admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        hash_pass = sha256(password.encode()).hexdigest()
        admin = Admin(email=email, password=hash_pass, id=1)
        self.app.database.admins.append(admin)
        return admin
