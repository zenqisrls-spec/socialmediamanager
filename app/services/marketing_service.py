from __future__ import annotations

from datetime import timedelta

from app.schemas import (
    AdsRequest,
    AdsResponse,
    CampaignIdea,
    ContentRequest,
    ContentResponse,
    PostIdea,
    ScheduleItem,
    ScheduleRequest,
    ScheduleResponse,
    StrategyRequest,
    StrategyResponse,
)
from app.services.ai_service import AIService


class MarketingService:
    def __init__(self) -> None:
        self.ai = AIService()

    def generate_strategy(self, payload: StrategyRequest) -> StrategyResponse:
        fallback = {
            "strategic_positioning": "ZenQi come riferimento locale per percorsi olistici integrati e personalizzati.",
            "monthly_pillars": [
                "Educazione al benessere olistico",
                "Testimonianze clienti e casi reali",
                "Promozione trattamenti e percorsi prova",
                "Community e fidelizzazione",
            ],
            "channel_mix": {
                "instagram": 40,
                "facebook": 30,
                "tiktok": 15,
                "linkedin": 15,
            },
            "kpis": [
                "Costo per lead",
                "Tasso di prenotazione prima consulenza",
                "Engagement rate",
                "Clienti di ritorno entro 60 giorni",
            ],
            "offer_funnel": [
                "Lead magnet: mini guida benessere",
                "Consulenza introduttiva",
                "Pacchetto 4 sedute",
                "Programma membership trimestrale",
            ],
        }

        result = self.ai.generate_json(
            "Sei un marketing strategist senior per centri olistici. Rispondi in JSON valido.",
            f"Genera una strategia per: {payload.json()}",
            fallback,
        )
        return StrategyResponse(**result)

    def generate_posts(self, payload: ContentRequest) -> ContentResponse:
        fallback_posts = []
        content_types = ["reel", "carousel", "stories", "post statico", "live teaser"]
        for idx in range(payload.posts_per_week):
            channel = payload.channels[idx % len(payload.channels)]
            goal = payload.goals[idx % len(payload.goals)]
            fallback_posts.append(
                {
                    "channel": channel,
                    "content_type": content_types[idx % len(content_types)],
                    "hook": f"3 segnali che il tuo corpo ti sta chiedendo equilibrio ({idx + 1})",
                    "caption": "Scopri una pratica semplice da inserire oggi per ridurre stress e ritrovare energia.",
                    "call_to_action": "Prenota la tua consulenza olistica su zenqi.it",
                    "objective": goal,
                }
            )

        fallback = {"post_ideas": fallback_posts}
        result = self.ai.generate_json(
            "Sei un social media manager per un centro olistico. Rispondi in JSON valido.",
            f"Crea idee post social per: {payload.json()}",
            fallback,
        )
        parsed = [PostIdea(**item) for item in result["post_ideas"]]
        return ContentResponse(post_ideas=parsed)

    def generate_campaigns(self, payload: AdsRequest) -> AdsResponse:
        daily_budget = round(payload.monthly_budget_eur / 30, 2)
        fallback = {
            "campaigns": [
                {
                    "platform": "Meta Ads",
                    "campaign_name": "ZenQi Lead - Consulenza Olistica",
                    "objective": "Lead generation",
                    "target_audience": "Donne e uomini 28-55 interessati a yoga, mindfulness, benessere naturale in area Roma",
                    "daily_budget_eur": daily_budget,
                    "ad_copy": "Ritrova equilibrio e benessere con un percorso personalizzato ZenQi.",
                    "creative_direction": "Video breve con testimonianza + scene ambiente del centro",
                    "kpi_target": "Costo per lead < 12 EUR",
                },
                {
                    "platform": "Google Ads",
                    "campaign_name": "ZenQi Search - Trattamenti Olistici Roma",
                    "objective": "Conversione prenotazioni",
                    "target_audience": "Persone che cercano trattamenti olistici e riduzione stress a Roma",
                    "daily_budget_eur": daily_budget,
                    "ad_copy": "Centro olistico a Roma: percorsi su misura per stress, energia e benessere.",
                    "creative_direction": "Annunci search con estensioni call e sitelink",
                    "kpi_target": "Tasso conversione landing > 6%",
                },
            ]
        }
        result = self.ai.generate_json(
            "Sei un media buyer senior. Rispondi in JSON valido.",
            f"Genera campagne per: {payload.json()}",
            fallback,
        )
        return AdsResponse(campaigns=[CampaignIdea(**item) for item in result["campaigns"]])

    def build_schedule(self, payload: ScheduleRequest) -> ScheduleResponse:
        slots = ["09:00", "13:00", "18:30", "21:00"]
        themes = [
            "Educazione olistica",
            "Dietro le quinte del centro",
            "Storia cliente",
            "Promo consulenza",
            "Routine benessere",
        ]
        items = []
        for week in range(payload.weeks):
            week_start = payload.start_date + timedelta(days=week * 7)
            for i in range(payload.posts_per_week):
                items.append(
                    ScheduleItem(
                        publication_date=week_start + timedelta(days=i % 7),
                        channel=payload.channels[i % len(payload.channels)],
                        slot=slots[i % len(slots)],
                        content_theme=themes[(week + i) % len(themes)],
                    )
                )

        return ScheduleResponse(items=items)
