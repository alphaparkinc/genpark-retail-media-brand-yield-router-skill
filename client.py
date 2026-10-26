# -*- coding: utf-8 -*-
"""
Glance Retail Media Brand Yield Router Client
Optimizes ad yield, eCPM, and GMV across L Catterton consumer portfolios, luxury fashion, and DTC retail media networks.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
from typing import Dict, Any, List

class GlanceRetailMediaBrandYieldRouter:
    """
    Generalized Second Price (GSP) auction router with quality score weighting,
    L Catterton consumer portfolio affinity multipliers, and hourly budget pacing.
    """

    def __init__(self, reserve_price_ecpm: float = 2.50):
        self.reserve_ecpm = reserve_price_ecpm

    def calculate_quality_score(self, ctr_historical: float, merchant_fulfillment_rating: float) -> float:
        """Computes composite ad quality factor (0.1 to 2.0)."""
        norm_ctr = min(2.0, max(0.2, (ctr_historical / 0.035)))
        norm_rating = min(1.0, max(0.5, merchant_fulfillment_rating / 5.0))
        return 0.65 * norm_ctr + 0.35 * norm_rating

    def calculate_portfolio_multiplier(self, brand_tier: str, user_cohort_wealth_index: float) -> float:
        """
        L Catterton consumer portfolio synergy: boost high-affinity luxury/DTC brands
        when the audience cohort exhibits strong purchasing power.
        """
        tier_weight = {
            "LUXURY_HERITAGE": 1.45,
            "PREMIUM_DTC": 1.25,
            "CONTEMPORARY_LIFESTYLE": 1.10,
            "MASS_MARKET": 0.95
        }.get(brand_tier.upper(), 1.0)

        wealth_boost = 1.0 + 0.35 * math.log(max(1.0, user_cohort_wealth_index))
        return tier_weight * wealth_boost

    def route_retail_media_bid(
        self,
        impression_context: Dict[str, Any],
        brand_campaign_bids: List[Dict[str, Any]] = None,
        pacing_hourly_budget_pct: float = 0.85
    ) -> Dict[str, Any]:
        """
        Executes real-time yield auction for Screen Zero retail media slot.
        """
        if brand_campaign_bids is None:
            brand_campaign_bids = [
                {
                    "campaign_id": "LCAT-BIRK-01",
                    "brand_name": "Birkenstock (L Catterton)",
                    "brand_tier": "PREMIUM_DTC",
                    "bid_cpc_usd": 1.80,
                    "target_cvr": 0.065,
                    "target_ctr": 0.048,
                    "aov_usd": 160.0,
                    "merchant_rating": 4.9,
                    "remaining_daily_budget_usd": 14500.0
                },
                {
                    "campaign_id": "LCAT-GANDI-02",
                    "brand_name": "Ganni (L Catterton)",
                    "brand_tier": "LUXURY_HERITAGE",
                    "bid_cpc_usd": 3.20,
                    "target_cvr": 0.052,
                    "target_ctr": 0.042,
                    "aov_usd": 380.0,
                    "merchant_rating": 4.8,
                    "remaining_daily_budget_usd": 22000.0
                },
                {
                    "campaign_id": "DTC-ALLB-03",
                    "brand_name": "Sustainable Wool Runner",
                    "brand_tier": "CONTEMPORARY_LIFESTYLE",
                    "bid_cpc_usd": 1.40,
                    "target_cvr": 0.045,
                    "target_ctr": 0.038,
                    "aov_usd": 110.0,
                    "merchant_rating": 4.6,
                    "remaining_daily_budget_usd": 8500.0
                },
                {
                    "campaign_id": "MASS-BEAUTY-04",
                    "brand_name": "Glow Hydration Mist",
                    "brand_tier": "MASS_MARKET",
                    "bid_cpc_usd": 0.90,
                    "target_cvr": 0.075,
                    "target_ctr": 0.055,
                    "aov_usd": 45.0,
                    "merchant_rating": 4.5,
                    "remaining_daily_budget_usd": 6000.0
                }
            ]

        wealth_idx = impression_context.get("user_cohort_wealth_index", 1.2)

        auction_ranks = []
        for bid in brand_campaign_bids:
            q_score = self.calculate_quality_score(
                bid.get("target_ctr", 0.03),
                bid.get("merchant_rating", 4.5)
            )
            portfolio_mult = self.calculate_portfolio_multiplier(
                bid.get("brand_tier", "MASS_MARKET"),
                wealth_idx
            )

            # Expected Effective CPM (eCPM) = 1000 * CTR * Bid_CPC * PortfolioMultiplier
            projected_ecpm = 1000.0 * bid.get("target_ctr", 0.03) * bid.get("bid_cpc_usd", 1.0) * portfolio_mult
            # Rank score integrates Quality and pacing factor
            pacing_factor = min(1.0, max(0.5, bid.get("remaining_daily_budget_usd", 1000.0) / 10000.0))
            rank_score = projected_ecpm * q_score * pacing_factor

            auction_ranks.append({
                "campaign_id": bid["campaign_id"],
                "brand_name": bid["brand_name"],
                "brand_tier": bid["brand_tier"],
                "projected_ecpm_usd": round(projected_ecpm, 2),
                "quality_score": round(q_score, 3),
                "portfolio_synergy_multiplier": round(portfolio_mult, 3),
                "rank_score": round(rank_score, 2),
                "projected_gmv_per_1k_imp_usd": round(1000.0 * bid.get("target_ctr", 0.03) * bid.get("target_cvr", 0.05) * bid.get("aov_usd", 100.0), 2)
            })

        # Sort descending by rank score
        auction_ranks.sort(key=lambda x: x["rank_score"], reverse=True)

        if not auction_ranks:
            return {"status": "NO_BIDS_AVAILABLE", "clearing_price_ecpm_usd": self.reserve_ecpm}

        winner = auction_ranks[0]
        runner_up = auction_ranks[1] if len(auction_ranks) > 1 else None

        # GSP Pricing: clearing price is set by runner-up rank score / winner's quality score
        if runner_up:
            clearing_ecpm = max(self.reserve_ecpm, round((runner_up["rank_score"] / winner["quality_score"]), 2))
        else:
            clearing_ecpm = self.reserve_ecpm

        return {
            "winning_campaign": {
                "campaign_id": winner["campaign_id"],
                "brand_name": winner["brand_name"],
                "brand_tier": winner["brand_tier"],
                "clearing_ecpm_usd": clearing_ecpm,
                "projected_gmv_per_1k_imp_usd": winner["projected_gmv_per_1k_imp_usd"]
            },
            "auction_efficiency_pct": round(min(100.0, (clearing_ecpm / max(0.01, winner["projected_ecpm_usd"])) * 100.0), 1),
            "reserve_price_ecpm_usd": self.reserve_ecpm,
            "ranked_auction_bids": auction_ranks
        }
