from __future__ import annotations

from pathlib import Path
import asyncio

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.schemas import (
    AppConfig,
    AdsRequest,
    AdsResponse,
    ContentRequest,
    ContentResponse,
    AutomationDraft,
    AutomationDraftCreateRequest,
    AutomationRunResponse,
    PublishedItem,
    PublishRequest,
    PublishResponse,
    ScheduleRequest,
    ScheduleResponse,
    StrategyRequest,
    StrategyResponse,
)
from app.services.app_config_service import AppConfigService
from app.services.automation_service import AutomationService
from app.services.marketing_service import MarketingService

app = FastAPI(
    title="ZenQi Social Media Manager API",
    description="Automazione AI per contenuti social e campagne advertising.",
    version="0.1.0",
)

service = MarketingService()
config_service = AppConfigService()
automation_service = AutomationService()
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"
automation_task: asyncio.Task | None = None


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


@app.post("/api/v1/automation/drafts", response_model=AutomationDraft)
def create_automation_draft(payload: AutomationDraftCreateRequest) -> AutomationDraft:
    item = automation_service.create_draft(payload.channel, payload.content, payload.scheduled_for)
    return AutomationDraft(**item)


@app.get("/api/v1/automation/drafts", response_model=list[AutomationDraft])
def get_automation_drafts(status: str | None = None) -> list[AutomationDraft]:
    return [AutomationDraft(**item) for item in automation_service.list_drafts(status=status)]


@app.post("/api/v1/automation/drafts/{draft_id}/approve", response_model=AutomationDraft)
def approve_automation_draft(draft_id: str) -> AutomationDraft:
    item = automation_service.approve(draft_id)
    if not item:
        raise HTTPException(status_code=404, detail="Draft non trovata")
    return AutomationDraft(**item)


@app.post("/api/v1/automation/drafts/{draft_id}/reject", response_model=AutomationDraft)
def reject_automation_draft(draft_id: str) -> AutomationDraft:
    item = automation_service.reject(draft_id)
    if not item:
        raise HTTPException(status_code=404, detail="Draft non trovata")
    return AutomationDraft(**item)


@app.get("/api/v1/automation/published", response_model=list[PublishedItem])
def get_published_items() -> list[PublishedItem]:
    return [PublishedItem(**item) for item in automation_service.list_published()]


@app.post("/api/v1/automation/run", response_model=AutomationRunResponse)
def run_automation_now() -> AutomationRunResponse:
    cfg = config_service.load()
    result = automation_service.run(
        require_human_approval=cfg.get("require_human_approval", True),
        autopublish_enabled=cfg.get("autopublish_enabled", False),
        whatsapp_enabled=cfg.get("whatsapp_enabled", False),
    )
    return AutomationRunResponse(**result)


async def _automation_loop() -> None:
    while True:
        cfg = config_service.load()
        automation_service.run(
            require_human_approval=cfg.get("require_human_approval", True),
            autopublish_enabled=cfg.get("autopublish_enabled", False),
            whatsapp_enabled=cfg.get("whatsapp_enabled", False),
        )
        await asyncio.sleep(30)


@app.on_event("startup")
async def _on_startup() -> None:
    global automation_task
    automation_task = asyncio.create_task(_automation_loop())


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    global automation_task
    if automation_task:
        automation_task.cancel()
