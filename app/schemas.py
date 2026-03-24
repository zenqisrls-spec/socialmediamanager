from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


SocialChannel = Literal["instagram", "facebook", "tiktok", "linkedin"]
GoalType = Literal["awareness", "lead_generation", "retention"]


class BusinessContext(BaseModel):
    brand_name: str = Field(default="ZenQi SRLS")
    website: str = Field(default="https://zenqi.it")
    industry: str = Field(default="Centro olistico")
    city: str = Field(default="Roma")
    unique_value: str = Field(
        default="Percorsi olistici personalizzati per benessere fisico, mentale ed energetico"
    )


class StrategyRequest(BaseModel):
    goals: list[GoalType] = Field(default_factory=lambda: ["awareness", "retention"])
    monthly_budget_eur: float = Field(default=1200, ge=0)
    context: BusinessContext = Field(default_factory=BusinessContext)


class StrategyResponse(BaseModel):
    strategic_positioning: str
    monthly_pillars: list[str]
    channel_mix: dict[SocialChannel, int]
    kpis: list[str]
    offer_funnel: list[str]


class ContentRequest(BaseModel):
    goals: list[GoalType]
    channels: list[SocialChannel]
    posts_per_week: int = Field(default=4, ge=1, le=14)
    tone_of_voice: str = Field(default="Empatico, autorevole, rassicurante")
    context: BusinessContext = Field(default_factory=BusinessContext)


class PostIdea(BaseModel):
    channel: SocialChannel
    content_type: str
    hook: str
    caption: str
    call_to_action: str
    objective: GoalType


class ContentResponse(BaseModel):
    post_ideas: list[PostIdea]


class AdsRequest(BaseModel):
    goals: list[GoalType]
    monthly_budget_eur: float = Field(default=1200, ge=100)
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


class AdsResponse(BaseModel):
    campaigns: list[CampaignIdea]


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
