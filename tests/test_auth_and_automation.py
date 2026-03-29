import os
from types import SimpleNamespace

from app.services.app_config_service import AppConfigService
from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.automation_service import AutomationService
from app.services.marketing_service import MarketingService
from app.schemas import AdsRequest, BusinessContext


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


def test_ai_service_reads_updated_config_without_restart(monkeypatch):
    cfg_service = AppConfigService()
    cfg = cfg_service.load()
    cfg["openai_api_key"] = "new-key-from-config"
    cfg["model_name"] = "gpt-4.1-mini"
    cfg_service.save(cfg)

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    ai = AIService()

    called = {}

    class FakeOpenAI:
        def __init__(self, api_key):
            called["api_key"] = api_key
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self._create)
            )

        @staticmethod
        def _create(**kwargs):
            called["model"] = kwargs["model"]
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))]
            )

    monkeypatch.setattr(AIService, "_create_client", staticmethod(FakeOpenAI))
    monkeypatch.setitem(os.environ, "OPENAI_API_KEY", "")
    monkeypatch.setitem(os.environ, "MODEL_NAME", "")
    result = ai.generate_json("sys", "usr", {"ok": False})

    assert result["ok"] is True
    assert called["api_key"] == "new-key-from-config"
    assert called["model"] == "gpt-4.1-mini"


def test_generate_campaigns_fallback_uses_payload_inputs(monkeypatch):
    cfg_service = AppConfigService()
    cfg = cfg_service.load()
    cfg["openai_api_key"] = ""
    cfg_service.save(cfg)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    service = MarketingService()
    payload = AdsRequest(
        goals=["awareness", "lead_generation"],
        monthly_budget_eur=1500,
        topics=["detox", "sonno"],
        context=BusinessContext(brand_name="LotusLab", city="Milano", unique_value="Percorsi bioenergetici personalizzati"),
    )
    result = service.generate_campaigns(payload)

    assert len(result.campaigns) == 2
    assert "LotusLab" in result.campaigns[0].campaign_name
    assert "Milano" in result.campaigns[0].target_audience
    assert "detox" in result.campaigns[0].ad_copy.lower()
