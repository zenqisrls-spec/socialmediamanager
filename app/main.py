from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.schemas import (
    AppConfig,
    AdsRequest,
    AdsResponse,
    ContentRequest,
    ContentResponse,
    PublishRequest,
    PublishResponse,
    ScheduleRequest,
    ScheduleResponse,
    StrategyRequest,
    StrategyResponse,
)
from app.services.app_config_service import AppConfigService
from app.services.marketing_service import MarketingService

app = FastAPI(
    title="ZenQi Social Media Manager API",
    description="Automazione AI per contenuti social e campagne advertising.",
    version="0.1.0",
)

service = MarketingService()
config_service = AppConfigService()
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"


@app.get("/", include_in_schema=False)
def web_ui() -> FileResponse:
    return FileResponse(WEB_INDEX)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/strategy/generate", response_model=StrategyResponse)
def generate_strategy(payload: StrategyRequest) -> StrategyResponse:
    return service.generate_strategy(payload)


@app.post("/api/v1/content/generate-posts", response_model=ContentResponse)
def generate_posts(payload: ContentRequest) -> ContentResponse:
    return service.generate_posts(payload)


@app.post("/api/v1/ads/generate-campaigns", response_model=AdsResponse)
def generate_campaigns(payload: AdsRequest) -> AdsResponse:
    return service.generate_campaigns(payload)


@app.post("/api/v1/scheduler/build", response_model=ScheduleResponse)
def build_schedule(payload: ScheduleRequest) -> ScheduleResponse:
    return service.build_schedule(payload)


@app.get("/api/v1/config", response_model=AppConfig)
def get_config() -> AppConfig:
    return AppConfig(**config_service.load())


@app.put("/api/v1/config", response_model=AppConfig)
def update_config(payload: AppConfig) -> AppConfig:
    return AppConfig(**config_service.save(payload.model_dump()))


@app.post("/api/v1/workflow/publish", response_model=PublishResponse)
def publish_with_approval(payload: PublishRequest) -> PublishResponse:
    cfg = config_service.load()
    if cfg.get("require_human_approval", True):
        return PublishResponse(
            status="pending_approval",
            message="Contenuto in coda: approvazione umana richiesta prima della pubblicazione.",
        )
    if not cfg.get("autopublish_enabled", False):
        return PublishResponse(
            status="blocked",
            message="Autopubblicazione disabilitata nelle configurazioni.",
        )
    return PublishResponse(
        status="simulated_published",
        message=f"Pubblicazione simulata su {payload.channel}. (Integrazione API social non ancora attiva).",
    )
