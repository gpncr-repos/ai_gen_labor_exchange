from typing import Iterable
from uuid import UUID

from sqlalchemy import select

from models.domain.aggregate_roots import Company
from models.domain.entities import Job
from models.domain.value_objects import UserInfo
from repositories.base_alchemy_repository import BaseAlchemyRepository
from storage.sqlalchemy.connection_proxy import AlchemyAsyncConnectionProxy
from storage.sqlalchemy.tables import Job as JobORM
from storage.sqlalchemy.tables import User


class CompanyRepository(BaseAlchemyRepository):
    def __init__(self, connection_proxy: AlchemyAsyncConnectionProxy):
        super().__init__(connection_proxy)

    async def create(self, *args, **kwargs) -> None:
        session = self.connection_proxy.connect()
        user_info = kwargs.get("user_info")
        company = User(
            email=user_info.email,
            name=user_info.name,
            hashed_password=user_info.hashed_password,
            is_company=True,
            created_at=user_info.created_at,
        )
        session.add(company)

    async def delete(self, *args, **kwargs) -> any:
        session = self.connection_proxy.connect()
        company_id = kwargs.get("id_")
        stmt = select(User).where(User.id == company_id)
        result = await session.execute(stmt)
        company = result.scalars().first()
        if company:
            await session.delete(company)
            return True
        return False

    async def list(self, *args, **kwargs) -> Iterable[any]:
        session = self.connection_proxy.connect()
        stmt = select(User).where(User.is_company == True)  # noqa
        result = await session.execute(stmt)
        return [
            Company(
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
        company_id = kwargs.get("id_")
        stmt = select(User).where(User.id == company_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            return Company(
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
        company_id = kwargs.get("id_")
        user_info = kwargs.get("user_info")
        stmt = select(User).where(User.id == company_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            user.email = user_info.email
            user.name = user_info.name
            user.hashed_password = user_info.hashed_password
            return True
        return False

    async def activate_job(self, job_id: UUID) -> None:
        session = self.connection_proxy.connect()
        stmt = select(JobORM).where(JobORM.id == job_id)
        result = await session.execute(stmt)
        job = result.scalars().first()
        if job:
            job.is_active = True

    async def add_job(self, job: Job) -> None:
        session = self.connection_proxy.connect()
        job_orm = JobORM(
            id=job.id,
            user_id=job.company_id,
            title=job.title,
            description=job.description,
            salary_from=job.salary_from,
            salary_to=job.salary_to,
            is_active=job.is_active,
            created_at=job.created_at,
        )
        session.add(job_orm)

    async def archive_job(self, job_id: UUID) -> None:
        session = self.connection_proxy.connect()
        stmt = select(JobORM).where(JobORM.id == job_id)
        result = await session.execute(stmt)
        job = result.scalars().first()
        if job:
            job.is_active = False

    async def delete_job(self, job_id: UUID) -> None:
        session = self.connection_proxy.connect()
        stmt = select(JobORM).where(JobORM.id == job_id)
        result = await session.execute(stmt)
        job = result.scalars().first()
        if job:
            await session.delete(job)

    async def update_job(self, job_id: UUID, updated_job: Job) -> None:
        session = self.connection_proxy.connect()
        stmt = select(JobORM).where(JobORM.id == job_id)
        result = await session.execute(stmt)
        job = result.scalars().first()
        if job:
            job.title = updated_job.title
            job.description = updated_job.description
            job.salary_from = updated_job.salary_from
            job.salary_to = updated_job.salary_to
            job.is_active = updated_job.is_active
