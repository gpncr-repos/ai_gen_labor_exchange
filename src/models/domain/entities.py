from __future__ import annotations  # noqa

import datetime
import uuid

from interfaces import base_domain_model as domain
from models.domain import value_objects


class Job(domain.DomainEntityObject):
    """
    Entity вакансии
    """

    def __init__(
        self,
        id_: uuid.UUID,
        company_id: uuid.UUID,
        title: str,
        description: str,
        salary_from: int,
        salary_to: int,
        is_active: bool,
        created_at: datetime.datetime,
    ):
        self._validate_salary(salary_from, salary_to)

        self.id = id_
        self.company_id = company_id
        self.title = title
        self.description = description
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.is_active = is_active
        self.created_at = created_at

        # словарь откликов, содержащий uuid соискателя (aggragate_root.Applicant)
        # и соответствующий список объектов откликов
        self.responses: dict[uuid.UUID, list[value_objects.Response]] = {}

    def _validate_salary(self, salary_from: int, salary_to: int):
        if salary_from <= 0 or salary_to <= 0:
            raise ValueError("Оклад не может быть отрицательным числом или равняться 0")

        if salary_from > salary_to:
            raise ValueError("Оклад должен задаваться в виде диапазона")

    def update_job(self, updated_job: Job) -> None:
        """
        Обновить данные о вакансии
        :param updated_job: обновленные данные о вакансии
        """

        self._validate_salary(updated_job.salary_from, updated_job.salary_to)

        self.title = updated_job.title
        self.description = updated_job.description
        self.salary_from = updated_job.salary_from
        self.salary_to = updated_job.salary_to
        self.is_active = updated_job.is_active

    def add_response(self, applicant_id: uuid.UUID, response: value_objects.Response):
        """
        Добавить отклик на вакансию
        """

        self.responses[applicant_id] = self.responses.get(applicant_id, [])
        self.responses[applicant_id].append(response)

    def delete_response(self, applicant_id: uuid.UUID, response: value_objects.Response):
        """
        Удалить отклик на вакансию
        """

        for response_num, response_ in self.responses[applicant_id]:
            if response.message == response_.message:
                del self.responses[applicant_id][response_num]
