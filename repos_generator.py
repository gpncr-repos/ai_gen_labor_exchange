from pathlib import Path

from ai_init_data.code_generator import generate_code, insert_into_project, save_result
from ai_init_data.prompt_data.repository_prompt import result as repository_prompt_result

if __name__ == "__main__":
    result = generate_code(repository_prompt_result)
    save_result(result, save_to=Path("ai_generated_data/generated_repos_result.json"))

    ai_result = Path("ai_generated_data/generated_repos_result.json")
    insert_to = Path("src/repositories")
    insert_into_project(ai_result, insert_to)
