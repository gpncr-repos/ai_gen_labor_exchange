from pathlib import Path

from ai_init_data.prompt_data import base_prompt_data

repositories_prompt_data = base_prompt_data.PromptData(
    entity="репозитории к моделям ORM из контекста",
    condition="для AggregateRoots: Applicant, Company из контекста (домен)",
    context=[
        base_prompt_data.ContextData(
            name="orm модели", file_path=Path("ai_init_data") / "orm" / "orm_models.txt"
        ),
        base_prompt_data.ContextData(
            name="домен", file_path=Path("ai_init_data") / "domain" / "domain.json"
        ),
        base_prompt_data.ContextData(
            name="базовые классы", file_path=Path("ai_init_data") / "interfaces" / "bases.json"
        ),
        base_prompt_data.ContextData(
            name="интерфейсы", file_path=Path("ai_init_data") / "interfaces" / "interfaces.json"
        ),
        base_prompt_data.ContextData(
            name="документация", file_path=Path("ai_init_data") / "docs" / "postgres-sqlalchemy.md"
        ),
    ],
    mandatory_rules=[
        "Реализуй все методы из 'BaseAlchemyRepository' для репозитория из контекста (базовые классы). Они не должны быть пустыми",  # noqa
        "Используй методы 'AlchemyAsyncConnectionProxy' из контекста (базовые классы).",
        "Используй `session.execute` для select запросов",
        "Используй документацию из контекста в качестве дополнительного источника информации (документация)",  # noqa
        "Репозитории должны быть построены только для AggregateRoot из контекста (домен)",
        "Репозитории должны возвращать AggregateRoot из контекста (домен)",  # noqa
        "Проанализируй и используй интерфейсы из контекста там где уместно (интерфейсы)",
        "Не используй промежуточные репозитории, обращайся к таблицам напрямую если это необходимо",
        "Реализуй в репозиториях дополнительные методы из AggregateRoots",
        "Импортируй AlchemyAsyncConnectionProxy из: `storage.sqlalchemy.connection_proxy`",
        "Импортируй ORM модели из: `storage.sqlalchemy.tables",
        "Импортируй BaseAlchemyRepository из: `repositories.base_alchemy_repository`",
    ],
    additional_rules=[
        "Один репозиторий = один файл",
        "Формат ответа: {'result': [{'filepath': 'model.py', 'code': 'код модели'}]}",
        "Если необходимо импортируй AggregateRoots из: `models.domain.aggregate_roots`",  # noqa
        "Если необходимо импортируй Value object из: `models.domain.value_objects`",
        "Если необходимо импортируй entities модели из: `models.domain.entities`",
        "Не делай session.commit()",
        "Не делай session.flush()",
        "Импортируй UserInfo из models.domain.value_objects",
    ],
)

result = base_prompt_data.generate_prompt(repositories_prompt_data)
