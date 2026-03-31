import os
from types import SimpleNamespace

from app.services.app_config_service import AppConfigService
from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.automation_service import AutomationService
from app.services.campaign_service import CampaignService
from app.services.marketing_service import MarketingService
from app.schemas import AdsRequest, BusinessContext, ContentRequest, StrategyRequest


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


def test_create_drafts_from_generated_posts():
    automation = AutomationService()
    created = automation.create_drafts_from_posts(
        [
            {
                "channel": "instagram",
                "hook": "Hook 1",
                "caption": "Caption 1",
                "call_to_action": "CTA 1",
            },
            {
                "channel": "facebook",
                "hook": "Hook 2",
                "caption": "Caption 2",
                "call_to_action": "CTA 2",
            },
        ]
    )
    assert len(created) == 2
    assert created[0]["channel"] == "instagram"
    assert "Caption 1" in created[0]["content"]


def test_campaign_batch_storage_and_status_update():
    service = CampaignService()
    created = service.create_batch(
        client_id="",
        name="Batch Test",
        notes="note",
        created_by="admin",
        campaigns=[
            {
                "platform": "Meta Ads",
                "campaign_name": "Campagna A",
                "objective": "Lead generation",
                "target_audience": "Target A",
                "daily_budget_eur": 30.0,
                "ad_copy": "copy A",
                "creative_direction": "creative A",
                "kpi_target": "CPL < 10",
            },
            {
                "platform": "Google Ads",
                "campaign_name": "Campagna B",
                "objective": "Brand awareness",
                "target_audience": "Target B",
                "daily_budget_eur": 20.0,
                "ad_copy": "copy B",
                "creative_direction": "creative B",
                "kpi_target": "CTR > 3%",
            },
        ],
    )
    assert created["name"] == "Batch Test"
    campaigns = service.list_campaigns(batch_id=created["batch_id"])
    assert len(campaigns) == 2
    updated = service.update_campaign_status(campaigns[0]["id"], "active")
    assert updated is not None
    assert updated["status"] == "active"


def test_strategy_generation_falls_back_when_ai_returns_invalid_shape(monkeypatch):
    service = MarketingService()

    def bad_generate_json(*args, **kwargs):
        return {"unexpected": "shape"}

    monkeypatch.setattr(service.ai, "generate_json", bad_generate_json)
    result = service.generate_strategy(
        StrategyRequest(
            client_id="",
            goals=["awareness"],
            monthly_budget_eur=1200,
            prompt_instructions="test",
            context=BusinessContext(brand_name="ClienteX", city="Milano"),
        )
    )
    assert result.strategic_positioning
    assert len(result.monthly_pillars) > 0


def test_content_generation_uses_fallback_when_ai_returns_empty(monkeypatch):
    service = MarketingService()

    def empty_generate_json(*args, **kwargs):
        return {}

    monkeypatch.setattr(service.ai, "generate_json", empty_generate_json)
    result = service.generate_posts(
        payload=ContentRequest(
            client_id="",
            goals=["awareness"],
            channels=["instagram"],
            posts_per_week=2,
            topics=["shiatsu"],
            prompt_instructions="test",
            context=BusinessContext(brand_name="ClienteY", website="https://y.it", city="Roma"),
        )
    )
    assert len(result.post_ideas) == 2
