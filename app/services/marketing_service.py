from __future__ import annotations

from datetime import timedelta
import re

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

    def generate_strategy(self, payload: StrategyRequest, runtime_config: dict | None = None) -> StrategyResponse:
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
            runtime_config=runtime_config,
        )
        try:
            return StrategyResponse(**result)
        except Exception:
            return StrategyResponse(**fallback)

    def generate_posts(self, payload: ContentRequest, runtime_config: dict | None = None) -> ContentResponse:
        fallback_posts = []
        content_types = ["reel", "carousel", "stories", "post statico", "live teaser"]
        topics = payload.topics or ["benessere olistico", "gestione dello stress", "energia quotidiana"]
        hook_templates = [
            "Se vivi a {city}: {topic} può cambiare la tua settimana",
            "{topic}: l'errore comune che vediamo ogni giorno a {city}",
            "{topic} senza miti: cosa funziona davvero per chi ha poco tempo",
            "3 segnali che indicano che è il momento di lavorare su {topic}",
            "Il metodo {brand}: {topic} con risultati misurabili in poche settimane",
        ]
        cta_templates = [
            "Scrivici in DM per una valutazione personalizzata.",
            "Prenota una consulenza iniziale dal sito.",
            "Contattaci su WhatsApp per capire il percorso più adatto.",
            "Salva il post e richiedi un piano personalizzato.",
        ]

        def _clean_hash(value: str) -> str:
            return re.sub(r"[^a-zA-Z0-9àèéìòùÀÈÉÌÒÙ]", "", value.replace(" ", ""))

        for idx in range(payload.posts_per_week):
            channel = payload.channels[idx % len(payload.channels)]
            goal = payload.goals[idx % len(payload.goals)]
            topic = topics[idx % len(topics)]
            hook = hook_templates[idx % len(hook_templates)].format(
                city=payload.context.city,
                topic=topic,
                brand=payload.context.brand_name,
            )
            caption = (
                f"{payload.context.brand_name} lavora ogni giorno con persone di {payload.context.city} su {topic}. "
                f"In questo contenuto condividiamo un consiglio pratico, chiaro e subito applicabile, "
                f"in linea con il nostro approccio: {payload.context.unique_value}."
            )
            cta = cta_templates[idx % len(cta_templates)]
            hashtags = [
                f"#{_clean_hash(topic).lower()}",
                f"#{_clean_hash(payload.context.city).lower()}",
                f"#{_clean_hash(payload.context.brand_name).lower()}",
            ]
            fallback_posts.append(
                {
                    "channel": channel,
                    "content_type": content_types[idx % len(content_types)],
                    "hook": hook,
                    "caption": caption,
                    "call_to_action": cta,
                    "objective": goal,
                    "image_prompt": f"Foto professionale lifestyle su tema {topic}, brand {payload.context.brand_name}, città {payload.context.city}, stile naturale.",
                    "image_url": self.ai.generate_image_url(
                        f"Immagine social per {payload.context.brand_name} su {topic} in {payload.context.city}",
                        runtime_config=runtime_config,
                    )
                    if payload.include_images
                    else "",
                    "final_post_text": (
                        f"{hook}\n\n"
                        f"{caption}\n\n"
                        f"{cta}\n"
                        f"{payload.context.website}\n\n"
                        f"{' '.join(hashtags)}"
                    ),
                    "hashtags": hashtags,
                    "visual_style": "Naturale, autentico, luminoso, orientato al benessere reale.",
                }
            )

        fallback = {"post_ideas": fallback_posts}
        result = self.ai.generate_json(
            (
                "Sei un social media strategist senior e copywriter direct-response. "
                "Scrivi in italiano professionale ma umano. "
                "Genera contenuti pronti per la pubblicazione, non bozze tecniche. "
                "Ogni post deve essere diverso per angolo, struttura e CTA. "
                "Contestualizza sempre su brand, città, settore, tono, obiettivi e argomenti."
            ),
            (
                f"Dati cliente e richiesta: {self._payload_json(payload)}.\n"
                f"Indicazioni specifiche del consulente: {payload.prompt_instructions}\n\n"
                "Restituisci SOLO JSON con chiave 'post_ideas' (array) e per ogni elemento questi campi:\n"
                "- channel\n- content_type\n- hook\n- caption\n- call_to_action\n- objective\n"
                "- image_prompt\n- image_url\n- final_post_text\n- hashtags (array di 3-6 hashtag)\n- visual_style\n\n"
                "Regole obbligatorie:\n"
                "1) final_post_text deve essere pronto da pubblicare.\n"
                "2) Evita frasi generiche e ripetitive.\n"
                "3) Inserisci riferimenti locali coerenti con la città del cliente.\n"
                "4) Non usare placeholder o testo template.\n"
                "5) Se include_images=true, image_prompt deve essere specifico e fotografabile."
            ),
            fallback,
            runtime_config=runtime_config,
        )
        for item in result.get("post_ideas", []):
            if payload.include_images and not item.get("image_url"):
                item["image_url"] = self.ai.generate_image_url(item.get("image_prompt", "social media image"), runtime_config=runtime_config)
            if not item.get("final_post_text"):
                item["final_post_text"] = f"{item.get('hook','')}\n\n{item.get('caption','')}\n\n{item.get('call_to_action','')}"
            if not item.get("hashtags"):
                topic = topics[0]
                item["hashtags"] = [
                    f"#{_clean_hash(topic).lower()}",
                    f"#{_clean_hash(payload.context.city).lower()}",
                    f"#{_clean_hash(payload.context.brand_name).lower()}",
                ]
            if not item.get("visual_style"):
                item["visual_style"] = "Naturale e autentico, coerente con il posizionamento del brand."
        raw_posts = result.get("post_ideas", []) or fallback_posts
        parsed = []
        for idx, item in enumerate(raw_posts):
            try:
                parsed.append(PostIdea(**item))
            except Exception:
                parsed.append(PostIdea(**fallback_posts[idx % len(fallback_posts)]))
        return ContentResponse(post_ideas=parsed)

    def generate_campaigns(self, payload: AdsRequest, runtime_config: dict | None = None) -> AdsResponse:
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
            runtime_config=runtime_config,
        )
        raw_campaigns = result.get("campaigns", []) or campaigns
        parsed_campaigns = []
        for idx, item in enumerate(raw_campaigns):
            try:
                parsed_campaigns.append(CampaignIdea(**item))
            except Exception:
                parsed_campaigns.append(CampaignIdea(**campaigns[idx % len(campaigns)]))
        return AdsResponse(campaigns=parsed_campaigns)

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
