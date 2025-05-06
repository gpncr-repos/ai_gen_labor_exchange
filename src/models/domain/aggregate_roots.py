import uuid

from interfaces import base_domain_model as domain
from models.domain import entities, value_objects


class UserBase(domain.DomainAggregate):
    """
    Базовый aggregate root для пользователей
    """

    def __init__(self, id_: uuid.UUID, user_info: value_objects.UserInfo):
        self.id = id_
        self.user_info = user_info


class Applicant(UserBase):
    """
    Aggregate root для соискателя
    """

    def __init__(self, id_: uuid.UUID, user_info: value_objects.UserInfo):
        super().__init__(id_, user_info)

        # словарь откликов, содержащий uuid вакансии (entities.Job)
        # и соответствующий список объектов откликов
        self.responses: dict[uuid.UUID, list[value_objects.Response]] = {}

    def add_response(self, job_id: uuid.UUID, response: value_objects.Response):
        """
        Добавить отклик на вакансию
        """

        self.responses[job_id] = self.responses.get(job_id, [])

        if len(self.responses[job_id]) > 5:
            raise ValueError("Превышен лимит откликов на одну вакансию")

        self.responses[job_id].append(response)

    def delete_response(self, job_id: uuid.UUID, response: value_objects.Response):
        """
        Удалить отклик на вакансию
        """

        for response_num, response_ in self.responses[job_id]:
            if response.message == response_.message:
                del self.responses[job_id][response_num]


class Company(UserBase):
    """
    Aggregate root для компании
    """

    def __init__(self, id_: uuid.UUID, user_info: value_objects.UserInfo):
        super().__init__(id_, user_info)

        # словарь вакансий, содержащий uuid вакансии и соответствующий объект вакансии
        self.jobs: dict[uuid.UUID, entities.Job] = {}

    def add_job(self, job: entities.Job):
        """
        Добавить вакансию
        """

        self.jobs[job.id] = job

    def update_job(self, job_id: uuid.UUID, updated_job: entities.Job) -> None:
        """
        Обновить данные о вакансии
        :param job_id: идентификатор вакансии
        :param updated_job: данные для обновления вакансии
        """

        self.jobs[job_id].update_job(updated_job)

    def delete_job(self, job_id: uuid.UUID):
        """
        Удалить вакансию
        """

        del self.jobs[job_id]

    def archive_job(self, job_id):
        """
        Заархивировать вакансию
        """

        self.jobs[job_id].is_active = False

    def activate_job(self, job_id):
        """
        Сделать вакансию активной
        """

        self.jobs[job_id].is_active = True
