from __future__ import annotations

from pathlib import Path
import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi import HTTPException
from fastapi import Header
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
    DashboardSummary,
    AuditLogItem,
    LoginRequest,
    LoginResponse,
    PublishedItem,
    PublishRequest,
    PublishResponse,
    ScheduleRequest,
    ScheduleResponse,
    StrategyRequest,
    StrategyResponse,
)
from app.services.app_config_service import AppConfigService
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
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
auth_service = AuthService()
audit_service = AuditService()
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"
automation_task: asyncio.Task | None = None


def get_current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Token mancante")
    token = authorization.split(" ", 1)[1]
    session = auth_service.validate(token)
    if not session:
        raise HTTPException(status_code=401, detail="Token non valido o scaduto")
    return session


def require_roles(user: dict, roles: set[str]) -> None:
    if user.get("role") not in roles:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")


@app.get("/", include_in_schema=False)
def web_ui() -> FileResponse:
    return FileResponse(WEB_INDEX)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    result = auth_service.login(payload.username, payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    return LoginResponse(**result)


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
def update_config(payload: AppConfig, user: dict = Depends(get_current_user)) -> AppConfig:
    require_roles(user, {"admin"})
    cfg = AppConfig(**config_service.save(payload.model_dump()))
    audit_service.log(user["username"], "update_config", "Configurazione aggiornata")
    return cfg


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
def create_automation_draft(payload: AutomationDraftCreateRequest, user: dict = Depends(get_current_user)) -> AutomationDraft:
    require_roles(user, {"admin", "editor"})
    item = automation_service.create_draft(payload.channel, payload.content, payload.scheduled_for)
    audit_service.log(user["username"], "create_draft", f"Draft {item['id']} creata")
    return AutomationDraft(**item)


@app.get("/api/v1/automation/drafts", response_model=list[AutomationDraft])
def get_automation_drafts(status: str | None = None) -> list[AutomationDraft]:
    return [AutomationDraft(**item) for item in automation_service.list_drafts(status=status)]


@app.post("/api/v1/automation/drafts/{draft_id}/approve", response_model=AutomationDraft)
def approve_automation_draft(draft_id: str, user: dict = Depends(get_current_user)) -> AutomationDraft:
    require_roles(user, {"admin", "approver"})
    item = automation_service.approve(draft_id)
    if not item:
        raise HTTPException(status_code=404, detail="Draft non trovata")
    audit_service.log(user["username"], "approve_draft", f"Draft {draft_id} approvata")
    return AutomationDraft(**item)


@app.post("/api/v1/automation/drafts/{draft_id}/reject", response_model=AutomationDraft)
def reject_automation_draft(draft_id: str, user: dict = Depends(get_current_user)) -> AutomationDraft:
    require_roles(user, {"admin", "approver"})
    item = automation_service.reject(draft_id)
    if not item:
        raise HTTPException(status_code=404, detail="Draft non trovata")
    audit_service.log(user["username"], "reject_draft", f"Draft {draft_id} rifiutata")
    return AutomationDraft(**item)


@app.get("/api/v1/automation/published", response_model=list[PublishedItem])
def get_published_items() -> list[PublishedItem]:
    return [PublishedItem(**item) for item in automation_service.list_published()]


@app.post("/api/v1/automation/run", response_model=AutomationRunResponse)
def run_automation_now(user: dict = Depends(get_current_user)) -> AutomationRunResponse:
    require_roles(user, {"admin"})
    cfg = config_service.load()
    result = automation_service.run(
        require_human_approval=cfg.get("require_human_approval", True),
        autopublish_enabled=cfg.get("autopublish_enabled", False),
        cfg=cfg,
    )
    audit_service.log(user["username"], "run_automation", str(result))
    return AutomationRunResponse(**result)


@app.get("/api/v1/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary() -> DashboardSummary:
    return DashboardSummary(**automation_service.summary())


@app.get("/api/v1/audit/logs", response_model=list[AuditLogItem])
def audit_logs(user: dict = Depends(get_current_user), limit: int = 100) -> list[AuditLogItem]:
    require_roles(user, {"admin"})
    return [AuditLogItem(**item) for item in audit_service.list_recent(limit=limit)]


async def _automation_loop() -> None:
    while True:
        cfg = config_service.load()
        automation_service.run(
            require_human_approval=cfg.get("require_human_approval", True),
            autopublish_enabled=cfg.get("autopublish_enabled", False),
            cfg=cfg,
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
