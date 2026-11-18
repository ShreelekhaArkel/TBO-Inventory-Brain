"""
smart_buyer.py - Demand Forecasting, Inventory Procurement Optimization & Risk Analysis
Takes the cleaned master catalog, forecasts upcoming demand using moving average and trend,
optimizes room block purchasing under an editable budget constraint, and computes financial
returns along with a -20% lower demand stress test.
"""

import pandas as pd
import numpy as np

def compute_demand_forecast(demand_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes upcoming demand forecast for each hotel using a 3-week Simple Moving Average
    (SMA) combined with recent trend momentum.
    """
    df = demand_df.copy()
    
    # Historical columns: week_1 through week_8
    forecasts = []
    trends = []
    sma_3w_list = []
    
    for _, row in df.iterrows():
        w6, w7, w8 = row["week_6"], row["week_7"], row["week_8"]
        sma_3 = (w6 + w7 + w8) / 3.0
        trend = w8 - w7
        # Projected upcoming demand: weighted blend of SMA and trend
        proj = round(0.70 * sma_3 + 0.30 * w8 + (0.4 * trend))
        forecast_val = max(5, int(proj))
        
        sma_3w_list.append(round(sma_3, 1))
        trends.append("Rising ↗" if trend > 0 else ("Falling ↘" if trend < 0 else "Stable →"))
        forecasts.append(forecast_val)
        
    df["sma_3_weeks"] = sma_3w_list
    df["demand_trend"] = trends
    df["forecasted_demand"] = forecasts
    return df

def optimize_purchasing(master_df: pd.DataFrame, forecasted_demand_df: pd.DataFrame, total_budget: float = 5000000.0, markup_pct: float = 0.20):
    """
    Allocates budget across master hotels based on forecasted demand and ranking score.
    Strictly guarantees that total purchasing cost <= total_budget.
    Simulates a 20% lower demand risk scenario.
    """
    # Merge master catalog with demand forecasts
    merged = master_df.merge(
        forecasted_demand_df[["master_hotel_id", "forecasted_demand", "demand_trend", "sma_3_weeks", "avg_weekly_demand"]],
        on="master_hotel_id",
        how="left"
    )
    
    # Priority sorting: higher rank score and higher demand get prioritized
    merged["priority_score"] = (
        merged["rank_score"] * 0.6 + 
        (merged["forecasted_demand"] / merged["forecasted_demand"].max() * 30) + 
        (merged["savings_pct"] * 0.1)
    )
    merged = merged.sort_values(by="priority_score", ascending=False).reset_index(drop=True)
    
    remaining_budget = float(total_budget)
    recommendations = []
    
    for _, row in merged.iterrows():
        procurement_unit = float(row["best_price_inr"])
        target_demand = int(row["forecasted_demand"])
        # Wholesale batch sizing: procure up to 22 rooms per hotel to ensure portfolio diversification
        # across luxury, mid-scale, and budget properties
        batch_target = min(target_demand, 22)
        suggested_selling = round(procurement_unit * (1.0 + markup_pct), -2)
        unit_profit = suggested_selling - procurement_unit
        
        # Determine room purchase quantity within available budget
        max_affordable_rooms = int(remaining_budget // procurement_unit)
        
        if max_affordable_rooms >= 3:
            rooms_to_buy = min(batch_target, max_affordable_rooms)
            total_cost = rooms_to_buy * procurement_unit
            remaining_budget -= total_cost
            status = "Purchased"
        else:
            rooms_to_buy = 0
            total_cost = 0.0
            status = "Excluded (Budget Cap)"
            
        expected_rev = rooms_to_buy * suggested_selling
        expected_profit = expected_rev - total_cost
        
        # 20% Downside Risk Scenario
        stressed_rooms_sold = int(np.floor(rooms_to_buy * 0.80))
        stressed_rev = stressed_rooms_sold * suggested_selling
        stressed_profit = stressed_rev - total_cost  # Cost was already committed
        risk_profit_loss = expected_profit - stressed_profit
        
        recommendations.append({
            "master_hotel_id": row["master_hotel_id"],
            "canonical_name": row["canonical_name"],
            "area": row["area"],
            "rating": row["rating"],
            "rank_score": row["rank_score"],
            "forecasted_demand": target_demand,
            "demand_trend": row["demand_trend"],
            "best_supplier": row["best_supplier"],
            "procurement_cost_unit": procurement_unit,
            "suggested_selling_price": suggested_selling,
            "unit_profit": unit_profit,
            "rooms_to_purchase": rooms_to_buy,
            "available_rooms": rooms_to_buy,  # Tracks live inventory deductible upon booking
            "total_investment": total_cost,
            "expected_revenue": expected_rev,
            "expected_profit": expected_profit,
            "status": status,
            # Risk scenario fields
            "stressed_rooms_sold": stressed_rooms_sold,
            "stressed_revenue": stressed_rev,
            "stressed_profit": stressed_profit,
            "profit_at_risk": risk_profit_loss
        })
        
    rec_df = pd.DataFrame(recommendations)
    
    # Financial Aggregates
    allocated_investment = rec_df["total_investment"].sum()
    expected_revenue = rec_df["expected_revenue"].sum()
    expected_profit = rec_df["expected_profit"].sum()
    utilization_pct = round((allocated_investment / total_budget) * 100, 1) if total_budget > 0 else 0.0
    roi_pct = round((expected_profit / allocated_investment) * 100, 1) if allocated_investment > 0 else 0.0
    
    # Stressed aggregates
    stressed_revenue = rec_df["stressed_revenue"].sum()
    stressed_profit = rec_df["stressed_profit"].sum()
    total_profit_at_risk = expected_profit - stressed_profit
    stressed_margin_pct = round((stressed_profit / stressed_revenue) * 100, 1) if stressed_revenue > 0 else 0.0
    
    purchased_count = len(rec_df[rec_df["status"] == "Purchased"])
    total_rooms_procured = rec_df["rooms_to_purchase"].sum()
    
    summary = {
        "total_budget": total_budget,
        "allocated_investment": allocated_investment,
        "remaining_budget": remaining_budget,
        "budget_utilization_pct": utilization_pct,
        "expected_revenue": expected_revenue,
        "expected_profit": expected_profit,
        "blended_roi_pct": roi_pct,
        "purchased_hotels_count": purchased_count,
        "total_rooms_procured": total_rooms_procured,
        # Risk summary
        "stressed_revenue": stressed_revenue,
        "stressed_profit": stressed_profit,
        "total_profit_at_risk": total_profit_at_risk,
        "stressed_margin_pct": stressed_margin_pct
    }
    
    return rec_df, summary

if __name__ == "__main__":
    from data_generator import generate_raw_supplier_listings, generate_historical_demand
    from catalog_cleaner import clean_and_merge_catalog
    
    raw = generate_raw_supplier_listings()
    master, comps, pairs, m = clean_and_merge_catalog(raw)
    demand = generate_historical_demand(master)
    forecasted_demand = compute_demand_forecast(demand)
    
    recs, summary = optimize_purchasing(master, forecasted_demand, total_budget=5000000)
    print("=== SMART BUYING SUMMARY ===")
    for k, v in summary.items():
        print(f"  {k}: {v:,.1f}" if isinstance(v, (int, float)) else f"  {k}: {v}")
        
    print("\nTop 5 Purchasing Recommendations:")
    print(recs[recs["status"] == "Purchased"][["canonical_name", "forecasted_demand", "procurement_cost_unit", "suggested_selling_price", "rooms_to_purchase", "total_investment", "expected_profit"]].head())
