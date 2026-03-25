from app.services.app_config_service import AppConfigService
from app.services.auth_service import AuthService
from app.services.automation_service import AutomationService


def test_login_and_token_validation():
    service = AuthService()
    payload = service.login("admin", "admin123")
    assert payload is not None
    session = service.validate(payload["access_token"])
    assert session is not None
    assert session["role"] == "admin"


def test_create_draft_and_summary():
    cfg = AppConfigService().load()
    automation = AutomationService()
    item = automation.create_draft("instagram", "pytest draft", None)
    assert item["status"] == "pending_approval"

    result = automation.run(
        require_human_approval=cfg["require_human_approval"],
        autopublish_enabled=cfg["autopublish_enabled"],
        cfg=cfg,
    )
    assert "processed" in result
    summary = automation.summary()
    assert summary["drafts_total"] >= 1

