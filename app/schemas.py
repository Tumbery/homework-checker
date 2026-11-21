from typing import Literal
from pydantic import BaseModel, Field


class CriterionResult(BaseModel):
    criterion: str = Field(description="Проверяемый критерий задания")
    score: float = Field(ge=0, le=10, description="Балл по критерию")
    comment: str


class HomeworkReview(BaseModel):
    overall_score: float = Field(ge=0, le=100, description="Итоговая оценка, %")
    grade: Literal["отлично", "хорошо", "удовлетворительно", "неудовлетворительно"]
    summary: str = Field(description="Краткое заключение для преподавателя")
    strengths: list[str]
    weaknesses: list[str]
    criteria: list[CriterionResult]
    estimated_effort_hours: float = Field(ge=0)
    plagiarism_risk: Literal["low", "medium", "high"]