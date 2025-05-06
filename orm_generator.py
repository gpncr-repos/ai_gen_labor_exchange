from pathlib import Path

from ai_init_data.code_generator import generate_code, insert_into_project, save_result
from ai_init_data.prompt_data.orm_prompt import result as orm_prompt_result

if __name__ == "__main__":
    result = generate_code(orm_prompt_result)
    save_result(result)

    ai_result = Path("ai_generated_data/generated_orm_result.json")
    insert_to = Path("src/storage/sqlalchemy/tables")
    insert_into_project(ai_result, insert_to)
