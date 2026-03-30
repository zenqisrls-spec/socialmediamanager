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

    @staticmethod
    def _payload_json(payload: object) -> str:
        if hasattr(payload, "model_dump_json"):
            return payload.model_dump_json()  # type: ignore[attr-defined]
        if hasattr(payload, "json"):
            return payload.json()  # type: ignore[attr-defined]
        return str(payload)

    def generate_strategy(self, payload: StrategyRequest) -> StrategyResponse:
        brand = payload.context.brand_name
        city = payload.context.city
        fallback = {
            "strategic_positioning": f"{brand} come riferimento locale per {payload.context.industry} in area {city}, con proposta distintiva centrata su {payload.context.unique_value}.",
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
            f"Genera una strategia per: {self._payload_json(payload)}. Indicazioni extra: {payload.prompt_instructions}",
            fallback,
        )
        return StrategyResponse(**result)

    def generate_posts(self, payload: ContentRequest) -> ContentResponse:
        fallback_posts = []
        content_types = ["reel", "carousel", "stories", "post statico", "live teaser"]
        topics = payload.topics or ["benessere olistico", "gestione dello stress", "energia quotidiana"]
        for idx in range(payload.posts_per_week):
            channel = payload.channels[idx % len(payload.channels)]
            goal = payload.goals[idx % len(payload.goals)]
            topic = topics[idx % len(topics)]
            fallback_posts.append(
                {
                    "channel": channel,
                    "content_type": content_types[idx % len(content_types)],
                    "hook": f"{topic.title()}: 3 segnali da non ignorare ({idx + 1})",
                    "caption": f"Scopri una pratica semplice su '{topic}' da inserire oggi per ridurre stress e ritrovare energia.",
                    "call_to_action": f"Prenota ora da {payload.context.brand_name} - {payload.context.website}",
                    "objective": goal,
                    "image_prompt": f"Foto professionale lifestyle su tema {topic}, brand {payload.context.brand_name}, città {payload.context.city}, stile naturale.",
                    "image_url": "",
                }
            )

        fallback = {"post_ideas": fallback_posts}
        result = self.ai.generate_json(
            "Sei un social media manager per un centro olistico. Rispondi in JSON valido.",
            f"Crea idee post social per: {self._payload_json(payload)}. Indicazioni extra: {payload.prompt_instructions}. Includi anche image_prompt e image_url (se disponibile).",
            fallback,
        )
        parsed = [PostIdea(**item) for item in result["post_ideas"]]
        return ContentResponse(post_ideas=parsed)

    def generate_campaigns(self, payload: AdsRequest) -> AdsResponse:
        daily_budget = round(payload.monthly_budget_eur / 30, 2)
        topics = payload.topics or ["benessere olistico personalizzato"]
        brand = payload.context.brand_name
        city = payload.context.city
        value = payload.context.unique_value

        objective_labels = {
            "lead_generation": "Lead generation",
            "awareness": "Brand awareness",
            "retention": "Retention",
        }

        campaigns = []
        for idx, goal in enumerate(payload.goals):
            topic = topics[idx % len(topics)]
            platform = "Meta Ads" if idx % 2 == 0 else "Google Ads"
            campaigns.append(
                {
                    "platform": platform,
                    "campaign_name": f"{brand} - {objective_labels.get(goal, goal)} - {topic.title()}",
                    "objective": objective_labels.get(goal, goal),
                    "target_audience": f"Persone interessate a {topic} in area {city}",
                    "daily_budget_eur": daily_budget,
                    "ad_copy": f"{brand}: {value}. Scopri il percorso su {topic} a {city}.",
                    "creative_direction": (
                        "Video verticale con testimonianza locale e CTA prenotazione"
                        if platform == "Meta Ads"
                        else "Annunci search geolocalizzati con estensioni di chiamata"
                    ),
                    "kpi_target": "Costo per lead < 12 EUR" if goal == "lead_generation" else "CTR > 3.5%",
                    "creative_brief_image": f"Visual campagna su {topic} ambientato a {city}, focus su risultato cliente e brand {brand}.",
                }
            )

        fallback = {"campaigns": campaigns}
        result = self.ai.generate_json(
            "Sei un media buyer senior. Rispondi in JSON valido.",
            f"Genera campagne per: {self._payload_json(payload)}. Indicazioni extra: {payload.prompt_instructions}. Includi creative_brief_image.",
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
