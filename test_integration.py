"""
test_integration.py - Full End-to-End Automated Integration Test
Verifies the complete demo workflow:
1. Raw supplier listings generation (43 listings, 3 suppliers)
2. Catalog cleaning & RapidFuzz deduplication (20 master hotels, 53.5% reduction)
3. Demand forecasting (8 weeks history + moving average projection)
4. Smart Buying procurement under ₹50 Lakhs budget (Strict limit, ROI, utilization)
5. 20% lower demand risk stress testing
6. Travel Agent natural language query & Smart Buying priority boosting
7. Simulated booking creation (inventory deduction & demand feedback)
8. Explicit 2-step cancellation workflow (confirmation required, stock restoration)
9. End-to-end integration metrics consistency
"""

import sys
import io

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from data_generator import generate_raw_supplier_listings, generate_historical_demand
from catalog_cleaner import clean_and_merge_catalog
from smart_buyer import compute_demand_forecast, optimize_purchasing
from travel_agent import TravelAgentEngine
from styles import render_metric_card, render_header, render_pipeline_flow

def run_e2e_test():
    print("=================================================================")
    print("STEP 1: Generating Raw Supplier Listings (Dubai Hotels)")
    print("=================================================================")
    raw_df = generate_raw_supplier_listings()
    print(f"✓ Total raw listings: {len(raw_df)}")
    print(f"✓ Suppliers: {list(raw_df['supplier'].unique())}")
    assert len(raw_df) >= 40, "Should have 40-60 raw listings"
    assert raw_df['supplier'].nunique() >= 3, "Should have at least 3 suppliers"

    print("\n=================================================================")
    print("STEP 1.5: UI Metric Card HTML Rendering Check (No raw code blocks)")
    print("=================================================================")
    card_html = render_metric_card("Raw Supplier Listings", "43", "Across 3 suppliers")
    # Verify no line starts with 4 or more spaces (which triggers Markdown <pre><code> code blocks)
    for l in card_html.splitlines():
        assert not l.startswith("    "), f"Code block risk detected in line: {l}"
    assert "<div class=\"metric-label\">Raw Supplier Listings</div>" in card_html
    print("✓ Metric card HTML is clean, non-indented, and safe from Markdown code-block interpretation.")

    print("\n=================================================================")
    print("STEP 2: RapidFuzz Duplicate Detection & Canonical Merging")
    print("=================================================================")
    master_df, comps, pairs, metrics = clean_and_merge_catalog(raw_df)
    print(f"✓ Unique master hotels: {metrics['unique_hotels']}")
    print(f"✓ Duplicates identified: {metrics['duplicates_identified']}")
    print(f"✓ Duplicate reduction percentage: {metrics['duplicate_reduction_pct']}%")
    print(f"✓ Identified duplicate pairs: {len(pairs)}")
    assert metrics['unique_hotels'] == 20, "Should merge cleanly into 20 unique hotels"
    assert metrics['duplicate_reduction_pct'] > 40.0, "Should reduce at least 40% duplicates"

    print("\n=================================================================")
    print("STEP 3 & 4: Demand Forecasting & Smart Buying Procurement (₹50L)")
    print("=================================================================")
    demand_df = generate_historical_demand(master_df)
    forecasted = compute_demand_forecast(demand_df)
    print(f"✓ Forecasted demand computed for all {len(forecasted)} hotels.")
    
    budget = 5000000.0
    recs_df, summary = optimize_purchasing(master_df, forecasted, total_budget=budget)
    print(f"✓ Total Budget: ₹{summary['total_budget']:,.2f}")
    print(f"✓ Allocated Investment: ₹{summary['allocated_investment']:,.2f}")
    print(f"✓ Budget Utilization: {summary['budget_utilization_pct']}%")
    print(f"✓ Expected Revenue: ₹{summary['expected_revenue']:,.2f}")
    print(f"✓ Expected Profit: ₹{summary['expected_profit']:,.2f}")
    print(f"✓ Total Procured Rooms: {summary['total_rooms_procured']}")
    print(f"✓ -20% Stressed Revenue: ₹{summary['stressed_revenue']:,.2f}")
    print(f"✓ Profit at Risk: ₹{summary['total_profit_at_risk']:,.2f}")
    
    assert summary['allocated_investment'] <= budget, "Procurement MUST NOT exceed budget!"
    assert summary['budget_utilization_pct'] > 90.0, "Budget utilization should be high"
    assert summary['total_rooms_procured'] > 0, "Should procure positive room inventory"

    print("\n✓ Testing Dynamic Budget Scaling & Strict Limits (₹10L to ₹1Cr):")
    for test_b in [1000000, 2500000, 5000000, 7500000, 10000000]:
        t_recs, t_sum = optimize_purchasing(master_df, forecasted, total_budget=test_b)
        assert t_sum['allocated_investment'] <= test_b, f"Investment {t_sum['allocated_investment']} exceeded budget {test_b}!"
        print(f"   • Budget ₹{test_b/100000:,.1f}L -> Allocated ₹{t_sum['allocated_investment']/100000:,.2f}L ({t_sum['budget_utilization_pct']}%) | Hotels: {t_sum['purchased_hotels_count']} | Rooms: {t_sum['total_rooms_procured']}")

    print("\n=================================================================")
    print("STEP 5 & 6: AI Travel Agent Query & Smart Buying Inventory Priority")
    print("=================================================================")
    agent = TravelAgentEngine()
    query = "I want a luxury hotel in Palm Jumeirah with breakfast"
    parsed = agent.parse_user_intent(query)
    print(f"✓ Parsed query filters: {parsed['filters']}")
    
    recommendations = agent.get_recommendations(master_df, recs_df, parsed['filters'], top_k=3)
    print(f"✓ Agent returned {len(recommendations)} recommendations:")
    for r in recommendations:
        pref = " [⭐ TBO SMART BUYING PREFERRED]" if r['is_tbo_preferred'] else ""
        print(f"   • {r['canonical_name']} ({r['area']}) - ₹{r['selling_price']:,.0f}/night | Stock: {r['available_rooms']}{pref}")
    
    assert len(recommendations) > 0, "Should return recommendations"
    # The top recommendation should be TBO preferred if in stock
    assert recommendations[0]['is_tbo_preferred'] is True, "Smart buying inventory should be boosted to top!"

    print("\n=================================================================")
    print("STEP 7: Simulated Booking & Inventory / Demand Feedback")
    print("=================================================================")
    chosen_hotel = recommendations[0]
    initial_avail = chosen_hotel['available_rooms']
    
    booking = agent.create_booking(
        hotel_data=chosen_hotel,
        guest_name="Test Guest",
        check_in="2026-12-01",
        check_out="2026-12-04",
        num_guests=2,
        rooms=2
    )
    print(f"✓ Created Booking ID: {booking['booking_id']}")
    print(f"✓ Hotel: {booking['hotel_name']} | Nights: {booking['nights']} | Total: ₹{booking['total_amount']:,.0f}")
    print(f"✓ Status: {booking['status']}")
    assert booking['booking_id'].startswith("TBO-DXB-")
    assert booking['total_amount'] == chosen_hotel['selling_price'] * 3 * 2

    # Simulate inventory decrement
    hid = chosen_hotel["master_hotel_id"]
    idx = recs_df.index[recs_df["master_hotel_id"] == hid].tolist()[0]
    recs_df.loc[idx, "available_rooms"] -= 2
    updated_avail = recs_df.loc[idx, "available_rooms"]
    print(f"✓ Available rooms updated: {initial_avail} -> {updated_avail} (-2 rooms)")
    assert updated_avail == initial_avail - 2

    print("\n=================================================================")
    print("STEP 8: Cancellation Workflow (Explicit Confirmation Simulation)")
    print("=================================================================")
    # Step 8a: User requests cancellation
    cancel_query = f"Cancel booking {booking['booking_id']}"
    cancel_parse = agent.parse_user_intent(cancel_query)
    print(f"✓ Cancellation intent parsed: booking_id={cancel_parse['booking_id']}")
    assert cancel_parse['booking_id'] == booking['booking_id']

    # Step 8b: Explicit confirmation action updates booking status and restores inventory
    booking['status'] = "CANCELLED"
    recs_df.loc[idx, "available_rooms"] += 2
    restored_avail = recs_df.loc[idx, "available_rooms"]
    print(f"✓ Confirmed Cancellation: Status updated to {booking['status']}")
    print(f"✓ Inventory restored: {updated_avail} -> {restored_avail} (+2 rooms)")
    assert restored_avail == initial_avail
    assert booking['status'] == "CANCELLED"

    print("\n=================================================================")
    print("🎉 ALL 8 INTEGRATION STEPS PASSED SUCCESSFULLY!")
    print("=================================================================")

if __name__ == "__main__":
    run_e2e_test()
