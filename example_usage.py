# -*- coding: utf-8 -*-
"""
Example usage of GlanceRetailMediaBrandYieldRouter
Demonstrates real-time GSP auction routing with L Catterton consumer portfolio weighting.
"""

from client import GlanceRetailMediaBrandYieldRouter

def main():
    router = GlanceRetailMediaBrandYieldRouter(reserve_price_ecpm=3.00)

    contexts = [
        {
            "name": "Impression A: High-Net-Worth Metropolitan Audience (Wealth Index 1.8)",
            "context": {"user_cohort_wealth_index": 1.8, "geo_market": "US_NYC"}
        },
        {
            "name": "Impression B: Mainstream Value-Conscious Mobile Cohort (Wealth Index 0.9)",
            "context": {"user_cohort_wealth_index": 0.9, "geo_market": "US_SUBURB"}
        }
    ]

    print("================================================================")
    print("Glance Retail Media Brand Yield Router - Live Runs")
    print("================================================================\n")

    for c in contexts:
        res = router.route_retail_media_bid(c["context"])
        win = res["winning_campaign"]
        print(f"[{c['name']}]")
        print(f"  Winning Brand          : {win['brand_name']} ({win['brand_tier']})")
        print(f"  Clearing eCPM          : ${win['clearing_ecpm_usd']:.2f}")
        print(f"  Projected GMV / 1k Imp : ${win['projected_gmv_per_1k_imp_usd']:.2f}")
        print(f"  Auction Efficiency     : {res['auction_efficiency_pct']}%\n")
        print("  Bidder Leaderboard:")
        for b in res["ranked_auction_bids"]:
            print(f"    * {b['brand_name']:<30} | RankScore: {b['rank_score']:>6.2f} | eCPM: ${b['projected_ecpm_usd']:>6.2f} | Synergy: {b['portfolio_synergy_multiplier']}x")
        print()

if __name__ == "__main__":
    main()
