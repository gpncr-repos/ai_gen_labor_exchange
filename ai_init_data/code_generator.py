import json
import os
from pathlib import Path

from openai import OpenAI

DEEPSEEK_API_KEY = os.environ.get("DS_API_KEY", None)
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"


def generate_code(prompt: str) -> dict:
    """
    Отправляет запрос к DeepSeek API и возвращает ответ в виде JSON.

    Параметры:
        prompt (str): Запрос на генерацию кода/текста.

    Возвращает:
        dict: Ответ API, включая сгенерированный контент и метаданные.
    """
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_BASE)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "Ты — Senior Python Developer. Твой ответ должен быть в JSON",
                },
                {"role": "user", "content": f"{prompt}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            top_p=0.9,
        )

        # Парсим JSON из текста ответа
        response_content = response.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        return {"error": str(e), "type": "API_ERROR"}


def save_result(
    result: dict, save_to: Path | None = Path("ai_generated_data/generated_orm_result.json")
) -> None:
    with open(save_to, "w") as f:
        f.write(json.dumps(result, indent=4))


def insert_into_project(ai_result: Path, insert_path: Path) -> None:
    with open(ai_result) as f:
        generated_json = json.load(f)
        result = generated_json["result"]

    for res in result:
        path = Path(res["filepath"]).name
        code = res["code"]
        with open(insert_path / path, "w") as f:
            f.write(code)
