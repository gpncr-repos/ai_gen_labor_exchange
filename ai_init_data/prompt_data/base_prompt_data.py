import dataclasses
import pathlib

_TEMPLATE = """
** Задание: Сгенерируй {entity} для {condition} на основе следующих условий.

** Контекст:
{context}

** Обязательные правила:
{mandatory_rules}

** Дополнительные правила:
{additional_rules}
"""

_CONTEXT_TEMPLATE = """
- {name}: {data}
"""

cwd_path = pathlib.Path.cwd()


@dataclasses.dataclass
class ContextData:
    name: str
    file_path: pathlib.Path


@dataclasses.dataclass
class PromptData:
    entity: str
    condition: str
    context: list[ContextData]
    mandatory_rules: list[str]
    additional_rules: list[str]


def generate_prompt(prompt_data: PromptData):
    context = []

    for data in prompt_data.context:
        with open(data.file_path, 'r', encoding='utf-8') as f:
            file_data = f.read()

        context.append(_CONTEXT_TEMPLATE.format(name=data.name, data=file_data))

    context = "\n".join(context)
    mandatory_rules = "\n".join(prompt_data.mandatory_rules)
    additional_rules = "\n".join(prompt_data.additional_rules)

    return _TEMPLATE.format(
        entity=prompt_data.entity,
        condition=prompt_data.condition,
        context=context,
        mandatory_rules=mandatory_rules,
        additional_rules=additional_rules
    )
