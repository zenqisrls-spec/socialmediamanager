from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


SocialChannel = Literal["instagram", "facebook", "tiktok", "linkedin"]
GoalType = Literal["awareness", "lead_generation", "retention"]


class BusinessContext(BaseModel):
    brand_name: str = Field(default="Brand Cliente")
    website: str = Field(default="https://example.com")
    industry: str = Field(default="Servizi")
    city: str = Field(default="Italia")
    unique_value: str = Field(
        default="Proposta di valore unica del cliente"
    )


class StrategyRequest(BaseModel):
    client_id: str = Field(default="")
    goals: list[GoalType] = Field(default_factory=lambda: ["awareness", "retention"])
    monthly_budget_eur: float = Field(default=1200, ge=0)
    prompt_instructions: str = Field(default="")
    context: BusinessContext = Field(default_factory=BusinessContext)


class StrategyResponse(BaseModel):
    strategic_positioning: str
    monthly_pillars: list[str]
    channel_mix: dict[SocialChannel, int]
    kpis: list[str]
    offer_funnel: list[str]


class ContentRequest(BaseModel):
    client_id: str = Field(default="")
    goals: list[GoalType]
    channels: list[SocialChannel]
    posts_per_week: int = Field(default=4, ge=1, le=14)
    topics: list[str] = Field(default_factory=list)
    tone_of_voice: str = Field(default="Empatico, autorevole, rassicurante")
    prompt_instructions: str = Field(default="")
    context: BusinessContext = Field(default_factory=BusinessContext)


class PostIdea(BaseModel):
    channel: SocialChannel
    content_type: str
    hook: str
    caption: str
    call_to_action: str
    objective: GoalType
    image_prompt: str = ""
    image_url: str = ""


class ContentResponse(BaseModel):
    post_ideas: list[PostIdea]


class ContentWithDraftsResponse(BaseModel):
    post_ideas: list[PostIdea]
    created_drafts: list["AutomationDraft"]


class AdsRequest(BaseModel):
    client_id: str = Field(default="")
    goals: list[GoalType]
    monthly_budget_eur: float = Field(default=1200, ge=100)
    topics: list[str] = Field(default_factory=list)
    prompt_instructions: str = Field(default="")
    context: BusinessContext = Field(default_factory=BusinessContext)


class CampaignIdea(BaseModel):
    platform: str
    campaign_name: str
    objective: str
    target_audience: str
    daily_budget_eur: float
    ad_copy: str
    creative_direction: str
    kpi_target: str
    creative_brief_image: str = ""


class AdsResponse(BaseModel):
    campaigns: list[CampaignIdea]


CampaignStatus = Literal["draft", "active", "paused", "completed", "archived"]


class CampaignBatchCreateRequest(BaseModel):
    client_id: str = ""
    name: str = Field(default="Batch campagne")
    notes: str = Field(default="")
    campaigns: list[CampaignIdea]


class CampaignBatch(BaseModel):
    id: str
    client_id: str = ""
    name: str
    created_by: str
    notes: str
    created_at: str


class CampaignRecord(CampaignIdea):
    id: str
    client_id: str = ""
    batch_id: str
    status: CampaignStatus
    created_at: str
    updated_at: str


class CampaignBatchResponse(BaseModel):
    batch_id: str
    name: str
    notes: str
    created_by: str
    created_at: str
    campaigns: list[CampaignRecord]


class CampaignStatusUpdateRequest(BaseModel):
    status: CampaignStatus


class ScheduleRequest(BaseModel):
    start_date: date
    weeks: int = Field(default=4, ge=1, le=12)
    channels: list[SocialChannel]
    posts_per_week: int = Field(default=4, ge=1, le=14)


class ScheduleItem(BaseModel):
    publication_date: date
    channel: SocialChannel
    slot: str
    content_theme: str


class ScheduleResponse(BaseModel):
    items: list[ScheduleItem]


class AppConfig(BaseModel):
    openai_api_key: str = ""
    model_name: str = "gpt-4.1-mini"
    require_human_approval: bool = True
    autopublish_enabled: bool = False
    whatsapp_enabled: bool = False
    meta_access_token: str = ""
    meta_page_id: str = ""
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_to: str = ""


class PublishRequest(BaseModel):
    channel: str
    content: str


class PublishResponse(BaseModel):
    status: str
    message: str


class AutomationDraftCreateRequest(BaseModel):
    client_id: str = ""
    channel: str
    content: str
    scheduled_for: str | None = None


class AutomationDraft(BaseModel):
    id: str
    client_id: str = ""
    channel: str
    content: str
    status: str
    scheduled_for: str
    created_at: str
    updated_at: str


class AutomationRunResponse(BaseModel):
    processed: int
    published: int
    failed: int


class PublishedItem(BaseModel):
    draft_id: str
    channel: str
    status: str
    message: str
    published_at: str


class DashboardSummary(BaseModel):
    drafts_total: int
    published_total: int
    published_ok: int
    published_failed: int
    drafts_by_status: dict[str, int]
    drafts_by_channel: dict[str, int]


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    role: str


class AuditLogItem(BaseModel):
    ts: str
    username: str
    action: str
    details: str


class AIStatus(BaseModel):
    api_key_configured: bool
    openai_package_available: bool


class ClientProfile(BaseModel):
    id: str
    name: str
    website: str = ""
    industry: str = ""
    city: str = ""
    unique_value: str = ""
    notes: str = ""
    openai_api_key: str = ""
    model_name: str = "gpt-4.1-mini"
    require_human_approval: bool = True
    autopublish_enabled: bool = False
    whatsapp_enabled: bool = False
    meta_access_token: str = ""
    meta_page_id: str = ""
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_to: str = ""
    created_at: str
    updated_at: str


class ClientProfileUpsert(BaseModel):
    name: str
    website: str = ""
    industry: str = ""
    city: str = ""
    unique_value: str = ""
    notes: str = ""
    openai_api_key: str = ""
    model_name: str = "gpt-4.1-mini"
    require_human_approval: bool = True
    autopublish_enabled: bool = False
    whatsapp_enabled: bool = False
    meta_access_token: str = ""
    meta_page_id: str = ""
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_to: str = ""
