from pathlib import Path

from ai_init_data.prompt_data import base_prompt_data

orm_prompt_data = base_prompt_data.PromptData(
    entity="orm-модель",
    condition="SQL Alchemy v.2",
    context=[
        base_prompt_data.ContextData(
            name="dbml-схема", file_path=Path("ai_init_data") / "dbml" / "dbml.txt"
        ),
        base_prompt_data.ContextData(
            name="домен", file_path=Path("ai_init_data") / "domain" / "domain.json"
        ),
    ],
    mandatory_rules=[
        "Явно импортируй: from sqlalchemy.orm import Mapped, mapped_column, relationship",
        "Обязательное использование Mapped[] и mapped_column() для всех полей",
        "ForeignKey должен быть внутри mapped_column()"
        "Для отношений используй аннотации типа: 1. Для many-to-one: Mapped['ParentModel'] = relationship(back_populates='children') 2.Для one-to-many: Mapped[list['ChildModel']] = relationship(back_populates='parent')",  # noqa
        "Все модели наследуются от Base (файл interfaces/base_alchemy_model.py)",
        "Без MappedAsDataclass",
        "Для nullable полей используй Mapped[type | None]",
        "Для отношений всегда указывай оба конца связи (back_populates)",
        "Внимательно проверь все back_populates, чтобы они ссылались на правильные атрибуты в связанных моделях",  # noqa
        "Не допускай циклических ссылок в back_populates",
        "Для отношений many-to-many используй ассоциативную таблицу",
    ],
    additional_rules=[
        "Одна модель = один файл",
        "Формат ответа: {'result': [{'filepath': 'model.py', 'code': 'код модели'}]}",
        "Все строковые поля должны иметь явную длину через String(length)",
        "Используй каскадное удаление",
    ],
)

result = base_prompt_data.generate_prompt(orm_prompt_data)
