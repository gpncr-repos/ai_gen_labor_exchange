from typing import Iterable
from uuid import UUID

from sqlalchemy import select

from models.domain.aggregate_roots import Applicant
from models.domain.value_objects import Response, UserInfo
from repositories.base_alchemy_repository import BaseAlchemyRepository
from storage.sqlalchemy.connection_proxy import AlchemyAsyncConnectionProxy
from storage.sqlalchemy.tables import Response as ResponseORM
from storage.sqlalchemy.tables import User


class ApplicantRepository(BaseAlchemyRepository):
    def __init__(self, connection_proxy: AlchemyAsyncConnectionProxy):
        super().__init__(connection_proxy)

    async def create(self, *args, **kwargs) -> None:
        session = self.connection_proxy.connect()
        user_info = kwargs.get("user_info")
        applicant = User(
            email=user_info.email,
            name=user_info.name,
            hashed_password=user_info.hashed_password,
            is_company=False,
            created_at=user_info.created_at,
        )
        session.add(applicant)

    async def delete(self, *args, **kwargs) -> any:
        session = self.connection_proxy.connect()
        applicant_id = kwargs.get("id_")
        stmt = select(User).where(User.id == applicant_id)
        result = await session.execute(stmt)
        applicant = result.scalars().first()
        if applicant:
            await session.delete(applicant)
            return True
        return False

    async def list(self, *args, **kwargs) -> Iterable[any]:
        session = self.connection_proxy.connect()
        stmt = select(User).where(User.is_company == False)  # noqa
        result = await session.execute(stmt)
        return [
            Applicant(
                id_=user.id,
                user_info=UserInfo(
                    email=user.email,
                    name=user.name,
                    hashed_password=user.hashed_password,
                    is_company=user.is_company,
                    created_at=user.created_at,
                ),
            )
            for user in result.scalars().all()
        ]

    async def retrieve(self, *args, **kwargs) -> any:
        session = self.connection_proxy.connect()
        applicant_id = kwargs.get("id_")
        stmt = select(User).where(User.id == applicant_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return Applicant(
                id_=user.id,
                user_info=UserInfo(
                    email=user.email,
                    name=user.name,
                    hashed_password=user.hashed_password,
                    is_company=user.is_company,
                    created_at=user.created_at,
                ),
            )
        return None

    async def update(self, *args, **kwargs) -> any:
        session = self.connection_proxy.connect()
        applicant_id = kwargs.get("id_")
        user_info = kwargs.get("user_info")
        stmt = select(User).where(User.id == applicant_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            user.email = user_info.email
            user.name = user_info.name
            user.hashed_password = user_info.hashed_password
            return True
        return False

    async def add_response(self, job_id: UUID, user_id: UUID, response: Response) -> None:
        session = self.connection_proxy.connect()
        response_orm = ResponseORM(job_id=job_id, user_id=user_id, message=response.message)
        session.add(response_orm)

    async def delete_response(self, job_id: UUID, user_id: UUID, response: Response) -> None:
        session = self.connection_proxy.connect()
        stmt = select(ResponseORM).where(
            ResponseORM.job_id == job_id,
            ResponseORM.user_id == user_id,
            ResponseORM.message == response.message,
        )
        result = await session.execute(stmt)
        response_orm = result.scalars().first()
        if response_orm:
            await session.delete(response_orm)
