import dataclasses
import datetime

from interfaces import base_domain_model as domain


@dataclasses.dataclass
class UserInfo(domain.DomainValueObject):
    """
    Value object, содержащий информацию о пользователе
    """

    email: str
    name: str
    hashed_password: str
    is_company: bool
    created_at: datetime.datetime


@dataclasses.dataclass
class Response(domain.DomainValueObject):
    """
    Value object, содержащий данные об отклике
    """

    message: str
