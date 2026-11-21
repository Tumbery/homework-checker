import os, json
from openai import OpenAI
from dotenv import load_dotenv
from .schemas import HomeworkReview

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "not-needed"),
)
MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")
PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

SYSTEM_PROMPT = (
    "Ты — цифровой сотрудник-ассистент преподавателя. Проверяешь домашние работы: "
    "оцениваешь по критериям, находишь ошибки, даёшь конструктивную обратную связь. "
    "Отвечай строго по заданной JSON-схеме, только по-русски. "
    "Никакого текста вне JSON, никаких markdown-обёрток."
)


def _strictify(schema: dict) -> dict:
    if "properties" in schema:
        schema["required"] = list(schema["properties"].keys())
        schema["additionalProperties"] = False
        for v in schema["properties"].values():
            _strictify(v)
    if "items" in schema:
        _strictify(schema["items"])
    return schema


def review_homework(assignment: str, student_work: str, temperature: float) -> HomeworkReview:
    schema = HomeworkReview.model_json_schema()
    for d in schema.get("$defs", {}).values():
        _strictify(d)
    schema = _strictify(schema)

    user_content = (
        f"Задание:\n{assignment}\n\n"
        f"Работа студента:\n{student_work}\n\n"
        f"Верни ответ СТРОГО в формате JSON по следующей схеме (без markdown, без пояснений):\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}"
    )

    kwargs = dict(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    if PROVIDER == "ollama":
        kwargs["response_format"] = {"type": "json_object"}
    else:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "homework_review", "schema": schema, "strict": True},
        }

    resp = client.chat.completions.create(**kwargs)
    raw = resp.choices[0].message.content

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    data = json.loads(raw)
    return HomeworkReview.model_validate(data)