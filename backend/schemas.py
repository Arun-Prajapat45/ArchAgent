from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, Field, field_validator, model_validator


class ChatRequest(BaseModel):
    user_input: str
    thread_id: str | None = None

    @field_validator("user_input")
    @classmethod
    def prompt_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("user_input must not be blank")
        return value.strip()


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ChatResponse(BaseModel):
    request_id: str
    thread_id: str
    output_requirements: str
    output_design: str
    output_code: str
    critique_iterations: int = Field(ge=0)
    estimated_monthly_cost_usd: float | None = Field(default=None, ge=0)
    cost_breakdown: list[str] = Field(default_factory=list)


class RequirementModel(BaseModel):
    archetype: str
    functional_requirements: list[str] = Field(min_length=1)
    non_functional_requirements: list[str] = Field(min_length=1)
    average_rps: int = Field(ge=0)
    peak_rps: int = Field(ge=0)

    @model_validator(mode="after")
    def peak_cannot_be_below_average(self) -> Self:
        if self.peak_rps < self.average_rps:
            raise ValueError("peak_rps must be greater than or equal to average_rps")
        return self


class Connectivity(BaseModel):
    source: str
    intermediary: str
    destination: str

    @model_validator(mode="before")
    @classmethod
    def accept_three_item_edge(cls, value: Any) -> Any:
        if isinstance(value, list) and len(value) == 3:
            return {"source": value[0], "intermediary": value[1], "destination": value[2]}
        return value
