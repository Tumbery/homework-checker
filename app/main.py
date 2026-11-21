from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .llm import review_homework
from .schemas import HomeworkReview

app = FastAPI(title="Homework Checker — цифровой сотрудник", version="0.1.0")


class CheckRequest(BaseModel):
    assignment: str = Field(description="Текст задания")
    student_work: str = Field(description="Ответ студента")
    temperature: float = Field(0.2, ge=0.0, le=1.0, description="Температура генерации")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/check-homework", response_model=HomeworkReview)
def check(req: CheckRequest):
    try:
        return review_homework(req.assignment, req.student_work, req.temperature)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ошибка LLM: {e}")