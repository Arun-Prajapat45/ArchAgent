from __future__ import annotations

import inspect
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable
from contextvars import ContextVar
from typing import Any, Protocol, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import Settings
from backend.costs import CostEstimator, InfracostClient
from backend.schemas import ChatRequest, ChatResponse
from backend.services import LegacyGraphService

request_id_context: ContextVar[str] = ContextVar("request_id", default="unknown")


class ArchitectureService(Protocol):
    def generate(self, prompt: str) -> dict[str, Any] | Awaitable[dict[str, Any]]: ...


class PricingService(Protocol):
    def estimate(self, design: dict[str, Any]) -> tuple[float | None, list[str]]: ...


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "request_id": request_id_context.get(),
            }
        )


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(logging.INFO)


def dict_to_markdown(data: dict[str, Any], level: int = 2) -> str:
    sections: list[str] = []
    for key, value in data.items():
        title = key.replace("_", " ").title()
        sections.append(f"{'#' * level} {title}\n")
        if isinstance(value, dict):
            sections.append(dict_to_markdown(value, level + 1))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    sections.append(dict_to_markdown(item, level + 1))
                else:
                    sections.append(f"- {item}\n")
        else:
            sections.append(f"{value}\n")
    return "\n".join(sections).strip()


def error_response(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": request_id}},
        headers={"X-Request-ID": request_id},
    )


def create_app(
    settings: Settings | None = None,
    architecture_service: ArchitectureService | None = None,
    pricing_service: PricingService | None = None,
) -> FastAPI:
    configure_logging()
    config = settings or Settings()
    architecture = architecture_service or LegacyGraphService()
    if pricing_service is None:
        client = (
            InfracostClient(config.infracost_api_key, config.external_timeout_seconds)
            if config.infracost_api_key
            else None
        )
        pricing: PricingService = CostEstimator(client)
    else:
        pricing = pricing_service

    application = FastAPI(
        title="ArchAgent API",
        version="0.1.0",
        description="RAG-assisted system requirements, HLD, critique, and Mermaid generation.",
    )
    application.state.settings = config
    application.state.architecture_service = architecture
    application.state.pricing_service = pricing

    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    request_times: dict[str, deque[float]] = defaultdict(deque)

    @application.middleware("http")
    async def request_context(request: Request, call_next: Any) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_context.set(request_id)
        try:
            if config.rate_limit_per_minute and request.url.path == "/chat":
                client_id = request.client.host if request.client else "unknown"
                now = time.monotonic()
                timestamps = request_times[client_id]
                while timestamps and now - timestamps[0] >= 60:
                    timestamps.popleft()
                if len(timestamps) >= config.rate_limit_per_minute:
                    return error_response(
                        429, "rate_limit_exceeded", "Too many requests", request_id
                    )
                timestamps.append(now)
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return cast(JSONResponse, response)
        finally:
            request_id_context.reset(token)

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        del request, exc
        return error_response(
            422,
            "validation_error",
            "Request body does not match the API schema",
            request_id_context.get(),
        )

    @application.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        del request
        logging.getLogger(__name__).exception("Unhandled request failure", exc_info=exc)
        return error_response(
            500, "internal_error", "The request could not be completed", request_id_context.get()
        )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/ready")
    async def ready() -> Any:
        if not config.ready:
            return error_response(
                503,
                "service_not_ready",
                "OPENROUTER_API_KEY is not configured",
                request_id_context.get(),
            )
        return {"status": "ready"}

    @application.post("/chat", response_model=ChatResponse)
    async def chat(payload: ChatRequest) -> Any:
        current_request_id = request_id_context.get()
        if not config.ready:
            return error_response(
                503,
                "service_not_ready",
                "OPENROUTER_API_KEY is not configured",
                current_request_id,
            )
        if len(payload.user_input) > config.max_prompt_chars:
            return error_response(
                413,
                "prompt_too_large",
                f"user_input exceeds {config.max_prompt_chars} characters",
                current_request_id,
            )

        result = architecture.generate(payload.user_input)
        if inspect.isawaitable(result):
            result = await result
        design = cast(dict[str, Any], result["design"])
        estimated_cost, breakdown = pricing.estimate(design)
        return ChatResponse(
            request_id=current_request_id,
            thread_id=payload.thread_id or str(uuid.uuid4()),
            output_requirements=dict_to_markdown(cast(dict[str, Any], result["requirements"])),
            output_design=dict_to_markdown(design),
            output_code=str(result["mermaid"]),
            critique_iterations=int(result.get("critique_iterations", 0)),
            estimated_monthly_cost_usd=estimated_cost,
            cost_breakdown=breakdown,
        )

    return application


app = create_app()
