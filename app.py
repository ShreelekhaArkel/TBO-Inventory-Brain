"""
app.py - TBO Inventory Brain Prototype
Main Streamlit Application
Modules:
1. Overview (Unified Pipeline & System Metrics)
2. Clean Catalog (RapidFuzz Deduplication, Merging & Ranking)
3. Smart Buying (Demand Forecasting, Knapsack Procurement & -20% Risk Analysis)
4. AI Travel Agent (Smart Inventory Prioritization, Booking Simulation & Strict 2-Step Cancellation)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

from state_manager import (
    initialize_system_state,
    run_catalog_cleaning,
    run_smart_buying,
    add_new_booking,
    execute_cancellation,
    get_pipeline_integration_metrics,
    DEFAULT_BUDGET
)
from styles import CUSTOM_CSS, render_header, render_pipeline_flow, render_metric_card

# Page Configuration
st.set_page_config(
    page_title="TBO Inventory Brain | Clean, Buy & Sell",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom Styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
initialize_system_state()

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.markdown("### **TBO Inventory Brain**")
    st.caption("Clean Inventory • Buy Smart • Sell AI")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["1. Overview", "2. Clean Catalog", "3. Smart Buying", "4. AI Travel Agent"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("#### **System Pipeline Status**")
    pipeline = get_pipeline_integration_metrics()
    st.markdown(f"• **Raw Listings:** `{pipeline['raw_total']}`")
    st.markdown(f"• **Clean Master Hotels:** `{pipeline['unique_master']}`")
    st.markdown(f"• **Procured Hotels:** `{pipeline['procured_hotels']}`")
    st.markdown(f"• **Available Inventory:** `{pipeline['available_procured_rooms']} / {pipeline['total_procured_rooms']} rooms`")
    st.markdown(f"• **Confirmed Bookings:** `{pipeline['confirmed_bookings_count']}`")
    st.markdown(f"• **Realized Revenue:** `₹{pipeline['live_revenue_realized']:,.0f}`")
    
    st.markdown("---")
    if st.button("🔄 Reset to Initial State"):
        st.session_state.clear()
        st.rerun()

# -------------------------------------------------------------------------------------------------
# PAGE 1: OVERVIEW
# -------------------------------------------------------------------------------------------------
if page == "1. Overview":
    st.markdown(
        render_header(
            "TBO Inventory Brain – Integrated Architecture Overview",
            "End-to-End Workflow: Clean supplier inventory, buy the right inventory, and sell it through an AI travel agent."
        ),
        unsafe_allow_html=True
    )
    st.markdown(render_pipeline_flow("Overview"), unsafe_allow_html=True)

    metrics = get_pipeline_integration_metrics()
    
    # 4 Key Metrics across modules
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            render_metric_card(
                "Catalog Health",
                f"{metrics['unique_master']} Hotels",
                f"From {metrics['raw_total']} raw listings ({metrics['duplicate_reduction_pct']}% deduplicated)",
                tag="Module 1"
            ),
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            render_metric_card(
                "Smart Procurement",
                f"₹{metrics['allocated_investment']/100000:,.2f} Lakhs",
                f"{metrics['available_procured_rooms']} available / {metrics['total_procured_rooms']} rooms across {metrics['procured_hotels']} hotels",
                tag="Module 2"
            ),
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            render_metric_card(
                "Projected Profit",
                f"₹{metrics['projected_profit']/100000:,.2f} Lakhs",
                f"Blended ROI: {metrics['blended_roi_pct']}% at standard markup",
                tag="Module 2"
            ),
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            render_metric_card(
                "Travel Agent Sales",
                f"₹{metrics['live_revenue_realized']:,.0f}",
                f"{metrics['confirmed_bookings_count']} confirmed bookings ({metrics['rooms_sold_live']} room-nights)",
                tag="Module 3"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # End-to-end Workflow Architecture Visualizer
    st.markdown("### 🔄 End-to-End Integration Flow")
    st.info(
        "**Core Architectural Principle:** All three modules share live synchronized data. "
        "Deduplicated supplier records supply master inventory to Smart Buying. "
        "Smart Buying procurement feeds prioritized inventory to the AI Travel Agent. "
        "Customer bookings in the Travel Agent deduct live procured room stock and dynamically update demand history."
    )

    col_chart, col_guide = st.columns([3, 2])
    with col_chart:
        # Dynamic Sankey diagram calculated directly from live shared state
        raw_df = st.session_state.raw_listings
        supp_counts = raw_df["supplier"].value_counts()
        s1_c = int(supp_counts.get("DirectBed Global", 0))
        s2_c = int(supp_counts.get("GulfTravel Wholesale", 0))
        s3_c = int(supp_counts.get("OasisRooms B2B", 0))
        
        proc_h_count = metrics["procured_hotels"]
        excl_h_count = metrics["unique_master"] - proc_h_count
        avail_rooms_count = metrics["available_procured_rooms"]
        sold_rooms_count = metrics["rooms_sold_live"]

        sankey_fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=18,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=[
                    f"DirectBed Global ({s1_c})",
                    f"GulfTravel ({s2_c})",
                    f"OasisRooms ({s3_c})",
                    f"Clean Master Catalog ({metrics['unique_master']})",
                    f"Smart Buying Procured ({proc_h_count})",
                    f"Excluded (Budget Cap) ({excl_h_count})",
                    f"AI Agent Sold ({sold_rooms_count} rooms)",
                    f"Available TBO Stock ({avail_rooms_count} rooms)"
                ],
                color=["#3B82F6", "#60A5FA", "#93C5FD", "#1E3A8A", "#10B981", "#94A3B8", "#0284C7", "#34D399"]
            ),
            link=dict(
                source=[0, 1, 2, 3, 3, 4, 4],
                target=[3, 3, 3, 4, 5, 6, 7],
                value=[
                    s1_c, s2_c, s3_c,
                    proc_h_count, excl_h_count,
                    max(1, sold_rooms_count),
                    max(1, avail_rooms_count)
                ],
                color=["#DBEAFE", "#DBEAFE", "#DBEAFE", "#A7F3D0", "#E2E8F0", "#BAE6FD", "#D1FAE5"]
            )
        )])
        sankey_fig.update_layout(
            title_text="Real-Time Inventory & Capital Allocation Flow",
            font_size=12,
            height=340,
            margin=dict(l=10, r=10, t=40, b=20)
        )
        st.plotly_chart(sankey_fig, use_container_width=True)

    with col_guide:
        st.markdown("#### 🎯 Hackathon Demo Workflow")
        st.markdown(
            """
            Follow these steps to demonstrate the complete integrated system:
            1. **Clean Catalog Tab:** Inspect raw listings across suppliers, run RapidFuzz duplicate detection, and review supplier price comparisons.
            2. **Smart Buying Tab:** Review forecasted weekly demand, edit the purchasing budget (default ₹50 Lakhs), and inspect the 20% downside risk scenario.
            3. **AI Travel Agent Tab:** Chat with the assistant, see how Smart Buying inventory is prioritized, and simulate a hotel booking.
            4. **Cancellation Flow:** Request cancellation to test the required 2-step explicit confirmation dialog and watch room stock restore.
            5. **Return to Overview:** Verify that live sales, bookings count, and demand feedback have updated automatically.
            """
        )

# -------------------------------------------------------------------------------------------------
# PAGE 2: CLEAN CATALOG
# -------------------------------------------------------------------------------------------------
elif page == "2. Clean Catalog":
    st.markdown(
        render_header(
            "Module 1: Clean Catalog & Deduplication",
            "Detect equivalent hotel listings across suppliers using RapidFuzz, merge them into master records, and rank them."
        ),
        unsafe_allow_html=True
    )
    st.markdown(render_pipeline_flow("Clean Catalog"), unsafe_allow_html=True)

    metrics = st.session_state.cleaning_metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_metric_card("Raw Supplier Listings", str(metrics["total_raw_listings"]), "Across 3 suppliers"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_metric_card("Unique Master Hotels", str(metrics["unique_hotels"]), "Distinct properties in Dubai"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_metric_card("Duplicates Identified", str(metrics["duplicates_identified"]), "Grouped into canonical entities"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_metric_card("Duplicate Reduction", f"{metrics['duplicate_reduction_pct']}%", "Catalog noise removed"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Subtabs for Clean Catalog
    tab_master, tab_compare, tab_raw, tab_dups = st.tabs([
        "🏨 Cleaned Master Catalog",
        "⚖️ Supplier Comparison View",
        "📄 Raw Supplier Feed",
        "🔍 RapidFuzz Duplicate Detection Analytics"
    ])

    with tab_master:
        st.markdown("#### Master Hotel Records (Ranked by Multi-Factor Score)")
        st.caption("Composite ranking incorporates Guest Rating (40%), Price Competitiveness (30%), Supplier Reliability (20%), and Offer Density (10%).")
        
        master_df = st.session_state.master_catalog.copy()
        
        # Area filter
        areas = ["All Areas"] + sorted(list(master_df["area"].unique()))
        selected_area = st.selectbox("Filter by Dubai Area:", areas, key="master_area_filter")
        if selected_area != "All Areas":
            master_df = master_df[master_df["area"] == selected_area]

        display_cols = [
            "master_hotel_id", "canonical_name", "area", "rating",
            "best_price_inr", "max_price_inr", "supplier_savings_inr",
            "best_supplier", "supplier_count", "match_confidence", "rank_score"
        ]
        
        # Format dataframe for presentation
        styled_df = master_df[display_cols].copy()
        styled_df["best_price_inr"] = styled_df["best_price_inr"].apply(lambda x: f"₹{x:,.0f}")
        styled_df["max_price_inr"] = styled_df["max_price_inr"].apply(lambda x: f"₹{x:,.0f}")
        styled_df["supplier_savings_inr"] = styled_df["supplier_savings_inr"].apply(lambda x: f"₹{x:,.0f}")
        styled_df["match_confidence"] = styled_df["match_confidence"].apply(lambda x: f"{x:.1f}%")
        styled_df.rename(columns={
            "master_hotel_id": "Hotel ID",
            "canonical_name": "Hotel Name",
            "area": "Area",
            "rating": "Rating",
            "best_price_inr": "Best Rate",
            "max_price_inr": "Highest Supplier Rate",
            "supplier_savings_inr": "Arbitrage Savings",
            "best_supplier": "Best Supplier",
            "supplier_count": "Offers",
            "match_confidence": "Match Conf.",
            "rank_score": "Rank Score"
        }, inplace=True)
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    with tab_compare:
        st.markdown("#### Multi-Supplier Price & Policy Comparison")
        st.caption("Select any cleaned master hotel to see the variations across suppliers.")
        
        hotel_options = {
            f"{row['master_hotel_id']} - {row['canonical_name']} ({row['area']})": row["master_hotel_id"]
            for _, row in st.session_state.master_catalog.iterrows()
        }
        chosen_hotel_str = st.selectbox("Select Hotel:", list(hotel_options.keys()), key="compare_hotel_select")
        chosen_hid = hotel_options[chosen_hotel_str]
        
        offers = st.session_state.supplier_comparisons.get(chosen_hid, [])
        master_row = st.session_state.master_catalog[st.session_state.master_catalog["master_hotel_id"] == chosen_hid].iloc[0]
        
        st.markdown(f"**Canonical Title:** `{master_row['canonical_name']}` | **Area:** `{master_row['area']}` | **Overall Rating:** `★ {master_row['rating']}`")
        st.markdown(f"**Max Arbitrage Spread:** `₹{master_row['supplier_savings_inr']:,.0f}` ({master_row['savings_pct']}% savings by booking via `{master_row['best_supplier']}`)")
        
        cols = st.columns(len(offers))
        for idx, off in enumerate(offers):
            is_best = (off["supplier"] == master_row["best_supplier"])
            border_color = "#2563EB" if is_best else "#E2E8F0"
            bg_color = "#F0FDF4" if is_best else "#FFFFFF"
            badge = "<span class='badge-procured'>⭐ Best Value Offer</span>" if is_best else ""
            
            with cols[idx]:
                card_html = (
                    f'<div style="border: 2px solid {border_color}; background: {bg_color}; border-radius: 10px; padding: 16px; height: 100%;">'
                    f'{badge}'
                    f'<h4 style="margin: 6px 0; color: #0F172A;">{off["supplier"]}</h4>'
                    f'<p style="font-size: 11px; color: #64748B; margin-bottom: 8px;">Supplier Reliability: <b>{int(off["supplier_reliability"]*100)}%</b></p>'
                    f'<div style="font-size: 22px; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">₹{off["price_inr"]:,.0f} <span style="font-size: 12px; font-weight: normal; color: #64748B;">/ night</span></div>'
                    f'<hr style="margin: 8px 0; border: none; border-top: 1px solid #CBD5E1;">'
                    f'<p style="font-size: 12px; margin: 4px 0;"><b>Listing Name:</b> {off["raw_name"]}</p>'
                    f'<p style="font-size: 12px; margin: 4px 0;"><b>Room:</b> {off["room_type"]}</p>'
                    f'<p style="font-size: 12px; margin: 4px 0;"><b>Meal Plan:</b> {off["meals"]}</p>'
                    f'<p style="font-size: 12px; margin: 4px 0;"><b>Cancellation:</b> {off["cancellation_policy"]}</p>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

    with tab_raw:
        st.markdown("#### Raw Supplier Ingestion Feed (43 Listings)")
        st.caption("Shows uncleaned raw listings from suppliers with naming variations, typos, and fragmented descriptions.")
        
        raw_df = st.session_state.raw_listings.copy()
        supplier_filter = st.multiselect("Filter Supplier:", raw_df["supplier"].unique(), default=raw_df["supplier"].unique())
        filtered_raw = raw_df[raw_df["supplier"].isin(supplier_filter)]
        
        st.dataframe(
            filtered_raw[["listing_id", "supplier", "hotel_name", "location", "price_inr", "rating", "meals", "cancellation_policy"]],
            use_container_width=True,
            hide_index=True
        )

    with tab_dups:
        st.markdown("#### RapidFuzz Matching Analytics & Confidence Scores")
        st.caption("Breakdown of string similarity across Brand Name, Location Address, and Descriptions for identified duplicate pairs.")
        
        pairs_df = st.session_state.pairwise_duplicates.copy()
        if not pairs_df.empty:
            c_left, c_right = st.columns([3, 2])
            with c_left:
                st.dataframe(
                    pairs_df[["listing_id_1", "hotel_1", "listing_id_2", "hotel_2", "name_similarity", "location_similarity", "confidence_score"]],
                    use_container_width=True,
                    hide_index=True
                )
            with c_right:
                fig_hist = px.histogram(
                    pairs_df,
                    x="confidence_score",
                    nbins=10,
                    title="Match Confidence Score Distribution (%)",
                    color_discrete_sequence=["#1E3A8A"]
                )
                fig_hist.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=20))
                st.plotly_chart(fig_hist, use_container_width=True)

# -------------------------------------------------------------------------------------------------
# PAGE 3: SMART BUYING
# -------------------------------------------------------------------------------------------------
elif page == "3. Smart Buying":
    st.markdown(
        render_header(
            "Module 2: Smart Buying & Inventory Optimization",
            "Forecast hotel demand, optimize purchasing within a dynamic budget, and simulate -20% demand risk."
        ),
        unsafe_allow_html=True
    )
    st.markdown(render_pipeline_flow("Smart Buying"), unsafe_allow_html=True)

    # Editable Budget Control
    b_col1, b_col2 = st.columns([2, 3])
    with b_col1:
        budget_input = st.number_input(
            "Purchasing Budget (₹ INR):",
            min_value=500000.0,
            max_value=20000000.0,
            value=float(st.session_state.purchasing_budget),
            step=250000.0,
            format="%.0f",
            help="Modifying this budget dynamically recalculates hotel purchasing allocations and risk metrics."
        )
        if budget_input != st.session_state.purchasing_budget:
            run_smart_buying(budget_input)
            st.rerun()

    with b_col2:
        st.markdown(f"**Current Allocation:** `₹{budget_input:,.0f}` (₹{budget_input/100000:,.1f} Lakhs)")
        st.caption("Greedy knapsack algorithm prioritizes high-demand, high-ROI canonical hotels up to the strict budget boundary.")

    summary = st.session_state.smart_buyer_summary
    recs_df = st.session_state.procurement_recommendations

    # KPI Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            render_metric_card(
                "Allocated Investment",
                f"₹{summary['allocated_investment']/100000:,.2f}L",
                f"Utilization: {summary['budget_utilization_pct']}% of ₹{summary['total_budget']/100000:.1f}L",
                tag="Safe Limit"
            ),
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            render_metric_card(
                "Expected Revenue",
                f"₹{summary['expected_revenue']/100000:,.2f}L",
                f"From {summary['total_rooms_procured']} procured room-nights",
                tag="20% Markup"
            ),
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            render_metric_card(
                "Expected Profit",
                f"₹{summary['expected_profit']/100000:,.2f}L",
                f"Blended Net ROI: {summary['blended_roi_pct']}%",
                tag="Base Case"
            ),
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            render_metric_card(
                "Downside Risk (-20%)",
                f"₹{summary['total_profit_at_risk']/100000:,.2f}L",
                f"Stress Revenue: ₹{summary['stressed_revenue']/100000:,.2f}L",
                tag="Stress Test"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Subtabs
    tab_recs, tab_forecast, tab_risk = st.tabs([
        "📋 Purchasing Recommendations",
        "📈 Demand Forecast & Time-Series",
        "⚠️ -20% Demand Risk Simulation"
    ])

    with tab_recs:
        st.markdown("#### Recommended Hotel Room Allocations")
        st.caption("Hotels marked 'Purchased' receive inventory funding and get prioritized in the AI Travel Agent.")
        
        display_recs = recs_df[[
            "canonical_name", "area", "rating", "forecasted_demand", "demand_trend",
            "procurement_cost_unit", "suggested_selling_price", "rooms_to_purchase",
            "available_rooms", "total_investment", "expected_profit", "status"
        ]].copy()
        
        display_recs["procurement_cost_unit"] = display_recs["procurement_cost_unit"].apply(lambda x: f"₹{x:,.0f}")
        display_recs["suggested_selling_price"] = display_recs["suggested_selling_price"].apply(lambda x: f"₹{x:,.0f}")
        display_recs["total_investment"] = display_recs["total_investment"].apply(lambda x: f"₹{x:,.0f}")
        display_recs["expected_profit"] = display_recs["expected_profit"].apply(lambda x: f"₹{x:,.0f}")
        
        display_recs.rename(columns={
            "canonical_name": "Hotel Name",
            "area": "Area",
            "rating": "Rating",
            "forecasted_demand": "Forecast Demand",
            "demand_trend": "Trend",
            "procurement_cost_unit": "Buy Price (Unit)",
            "suggested_selling_price": "Sell Price (Unit)",
            "rooms_to_purchase": "Rooms Procured",
            "available_rooms": "Available Stock",
            "total_investment": "Total Capital",
            "expected_profit": "Expected Profit",
            "status": "Procurement Status"
        }, inplace=True)
        
        st.dataframe(display_recs, use_container_width=True, hide_index=True)

    with tab_forecast:
        st.markdown("#### Historical Weekly Demand & Moving Average Projections")
        st.caption("Demand time-series for the past 8 weeks alongside trend projection for the upcoming cycle.")
        
        d_df = st.session_state.demand_history
        hotel_list = list(d_df["canonical_name"].unique())
        chosen_h_demand = st.selectbox("Select Hotel for Demand Curve:", hotel_list, key="demand_hotel_curve")
        
        h_row = d_df[d_df["canonical_name"] == chosen_h_demand].iloc[0]
        weeks = [f"Week {i}" for i in range(1, 9)]
        values = [h_row[f"week_{i}"] for i in range(1, 9)]
        
        # Next cycle forecast
        fc_val = st.session_state.forecasted_demand[st.session_state.forecasted_demand["canonical_name"] == chosen_h_demand]["forecasted_demand"].iloc[0]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weeks, y=values,
            mode="lines+markers",
            name="Historical Bookings",
            line=dict(color="#1E3A8A", width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=["Week 8", "Forecast (Next Cycle)"],
            y=[values[-1], fc_val],
            mode="lines+markers",
            name="Upcoming Forecast",
            line=dict(color="#059669", width=3, dash="dot"),
            marker=dict(size=10, symbol="star")
        ))
        fig.update_layout(
            title=f"Demand History & Projection: {chosen_h_demand} (Forecast: {fc_val} rooms)",
            xaxis_title="Timeline",
            yaxis_title="Weekly Room Demand",
            height=380,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_risk:
        st.markdown("#### Downside Risk Analysis: -20% Demand Scenario")
        st.caption("Stress tests the investment portfolio assuming market-wide demand contracts by 20%.")
        
        purchased_subset = recs_df[recs_df["status"] == "Purchased"]
        
        r_c1, r_c2 = st.columns([3, 2])
        with r_c1:
            fig_bar = go.Figure(data=[
                go.Bar(name='Base Expected Profit', x=purchased_subset["canonical_name"], y=purchased_subset["expected_profit"], marker_color='#10B981'),
                go.Bar(name='Stressed Profit (-20% Demand)', x=purchased_subset["canonical_name"], y=purchased_subset["stressed_profit"], marker_color='#F59E0B')
            ])
            fig_bar.update_layout(
                barmode='group',
                title="Profit Comparison: Base Case vs 20% Demand Contraction",
                xaxis_tickangle=-45,
                height=360,
                margin=dict(l=20, r=20, t=40, b=80)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with r_c2:
            risk_box_html = (
                f'<div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 18px;">'
                f'<h4 style="color: #92400E; margin-top: 0;">⚠️ Risk Vulnerability Report</h4>'
                f'<p style="font-size: 13px; color: #78350F;">If travel demand to Dubai falls by 20%:</p>'
                f'<ul style="font-size: 13px; color: #78350F; padding-left: 20px;">'
                f'<li><b>Rooms Sold:</b> Drops from {summary["total_rooms_procured"]} to {int(purchased_subset["stressed_rooms_sold"].sum())} rooms</li>'
                f'<li><b>Revenue Realized:</b> Drops from ₹{summary["expected_revenue"]:,.0f} to ₹{summary["stressed_revenue"]:,.0f}</li>'
                f'<li><b>Capital at Risk:</b> ₹{summary["total_profit_at_risk"]:,.0f} in unrealized profit</li>'
                f'<li><b>Stressed Net Profit:</b> ₹{summary["stressed_profit"]:,.0f}</li>'
                f'</ul>'
                f'<div style="font-size: 12px; color: #B45309; background: #FEF3C7; padding: 8px 12px; border-radius: 6px;">'
                f'<b>Safety Buffer:</b> TBO maintains positive unit margins on fast-moving inventory; high-value luxury suites exhibit the highest downside variance.'
                f'</div>'
                f'</div>'
            )
            st.markdown(risk_box_html, unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------
# PAGE 4: AI TRAVEL AGENT
# -------------------------------------------------------------------------------------------------
elif page == "4. AI Travel Agent":
    st.markdown(
        render_header(
            "Module 3: AI Travel Agent & Booking Management",
            "Interactive assistant recommending verified inventory, prioritizing Smart Buying purchases, and handling bookings."
        ),
        unsafe_allow_html=True
    )
    st.markdown(render_pipeline_flow("AI Travel Agent"), unsafe_allow_html=True)

    agent_engine = st.session_state.agent_engine
    master_df = st.session_state.master_catalog
    smart_recs = st.session_state.procurement_recommendations

    col_chat, col_manage = st.columns([3, 2])

    with col_chat:
        st.markdown("### 💬 Conversational Travel Assistant")
        st.caption("Ask for recommendations based on budget, dates, location, or amenities.")
        
        # Quick prompts
        st.markdown("**Quick Inquiries:**")
        qp_cols = st.columns(4)
        quick_query = None
        if qp_cols[0].button("🏖️ Palm Jumeirah Luxury", key="qp1"):
            quick_query = "Luxury hotel in Palm Jumeirah with breakfast"
        if qp_cols[1].button("🌆 Downtown < ₹20,000", key="qp2"):
            quick_query = "Hotel in Downtown Dubai under 20000"
        if qp_cols[2].button("💼 Business Bay 4-Star", key="qp3"):
            quick_query = "Business Bay hotel with free cancellation"
        if qp_cols[3].button("📋 View My Bookings", key="qp4"):
            quick_query = "View my active bookings"

        # Render chat history
        chat_container = st.container(height=440)
        with chat_container:
            for m_idx, msg in enumerate(st.session_state.chat_messages):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if "recommendations" in msg and msg["recommendations"]:
                        for r_idx, rec in enumerate(msg["recommendations"]):
                            is_pref = rec.get("is_tbo_preferred", False)
                            pref_badge = "<span class='badge-procured'>⭐ TBO Strategic Inventory (Instant Guarantee)</span>" if is_pref else "<span style='color: #64748B; font-size: 11px;'>Standard B2B Catalog</span>"
                            avail_text = f"• Stock: <b>{rec.get('available_rooms', 0)} rooms available</b>" if is_pref else ""
                            
                            hotel_card_html = (
                                f'<div class="hotel-card {"preferred" if is_pref else ""}">'
                                f'{pref_badge}'
                                f'<div class="hotel-title">{rec["canonical_name"]} ★ {rec["rating"]}</div>'
                                f'<div class="hotel-meta">📍 {rec["area"]} | 🍽️ {rec["meals"]} | 🛡️ {rec["cancellation_policy"]} {avail_text}</div>'
                                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                                f'<div><span class="hotel-price">₹{rec["selling_price"]:,.0f}</span><span style="font-size: 12px; color: #64748B;"> / night</span></div>'
                                f'<div style="font-size: 11px; color: #059669; font-weight: 600;">Fulfilled by: {rec["best_supplier"]}</div>'
                                f'</div>'
                                f'</div>'
                            )
                            st.markdown(hotel_card_html, unsafe_allow_html=True)
                            if st.button(f"⚡ Select {rec['canonical_name']} for Booking", key=f"btn_pick_{rec['master_hotel_id']}_{m_idx}_{r_idx}"):
                                st.session_state.selected_booking_hotel = rec["canonical_name"]
                                st.rerun()

        # Chat Input
        user_input = st.chat_input("Ask for hotel recommendations or enter booking/cancellation commands...")
        active_query = quick_query if quick_query else user_input

        if active_query:
            # Append user message
            st.session_state.chat_messages.append({"role": "user", "content": active_query})
            parsed = agent_engine.parse_user_intent(active_query)

            if parsed["intent"] == "cancel_request":
                booking_id = parsed.get("booking_id")
                if booking_id:
                    st.session_state.pending_cancellation_id = booking_id
                    reply_text = f"⚠️ **Cancellation Requested for {booking_id}**\n\n**Explicit Confirmation Required:** Please review the reservation details in the right-hand panel and click **Confirm Cancellation** to proceed."
                else:
                    reply_text = "Please specify the Booking ID you would like to cancel (e.g., *'Cancel TBO-DXB-12345'*), or click Cancel next to the reservation in the Active Bookings panel."
                st.session_state.chat_messages.append({"role": "assistant", "content": reply_text})
                st.rerun()

            elif parsed["intent"] == "view_bookings":
                b_list = [b for b in st.session_state.bookings if b["status"] == "CONFIRMED"]
                if b_list:
                    items_str = "\n".join([f"• **{b['booking_id']}**: {b['hotel_name']} ({b['nights']} nights, ₹{b['total_amount']:,.0f})" for b in b_list])
                    reply_text = f"You currently have **{len(b_list)} active booking(s)**:\n{items_str}\n\nTo cancel any booking, say *'Cancel <Booking-ID>'* or click Cancel on the right."
                else:
                    reply_text = "You currently have no active bookings."
                st.session_state.chat_messages.append({"role": "assistant", "content": reply_text})
                st.rerun()

            elif parsed["intent"] == "book_request":
                hotel_ref = parsed.get("hotel_ref")
                matched_h = None
                if hotel_ref:
                    matched_h = master_df[master_df["master_hotel_id"] == hotel_ref]
                if matched_h is None or matched_h.empty:
                    for _, h in master_df.iterrows():
                        if h["canonical_name"].lower() in active_query.lower() or any(w in active_query.lower() for w in h["canonical_name"].lower().split() if len(w) > 4):
                            matched_h = pd.DataFrame([h])
                            break

                if matched_h is not None and not matched_h.empty:
                    h_row = matched_h.iloc[0]
                    st.session_state.selected_booking_hotel = h_row["canonical_name"]
                    proc_match = smart_recs[smart_recs["master_hotel_id"] == h_row["master_hotel_id"]]
                    is_p = False
                    s_price = round(h_row["best_price_inr"] * 1.20, -2)
                    if not proc_match.empty and proc_match.iloc[0]["status"] == "Purchased":
                        is_p = True
                        s_price = proc_match.iloc[0]["suggested_selling_price"]

                    hotel_payload = {
                        "master_hotel_id": h_row["master_hotel_id"],
                        "canonical_name": h_row["canonical_name"],
                        "area": h_row["area"],
                        "selling_price": s_price,
                        "best_supplier": h_row["best_supplier"],
                        "meals": h_row["best_meals"],
                        "cancellation_policy": h_row["best_cancellation"],
                        "room_type": h_row["best_room_type"],
                        "is_tbo_preferred": is_p
                    }
                    today_val = date.today()
                    cin = str(today_val + timedelta(days=7))
                    cout = str(today_val + timedelta(days=10))
                    new_b = add_new_booking(
                        hotel_data=hotel_payload,
                        guest_name="Rahul Sharma",
                        check_in=cin,
                        check_out=cout,
                        num_guests=2,
                        rooms=1
                    )
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": (
                            f"🎉 **Simulated Booking Confirmed!**\n\n"
                            f"• **Booking ID:** `{new_b['booking_id']}`\n"
                            f"• **Hotel:** {new_b['hotel_name']} ({new_b['area']})\n"
                            f"• **Guest:** {new_b['guest_name']}\n"
                            f"• **Stay:** {new_b['check_in']} to {new_b['check_out']} ({new_b['nights']} nights)\n"
                            f"• **Total Amount:** ₹{new_b['total_amount']:,.0f}\n"
                            f"• **Inventory Feedback:** 1 room deducted from Smart Buying stock.\n\n"
                            f"Your reservation is now active in the system!"
                        )
                    })
                else:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": "Please specify the hotel name you would like to book (e.g., *'Book Atlantis The Palm'* or *'Book Sofitel'*), or select it from the booking panel on the right."
                    })
                st.rerun()

            else:
                # Recommendation query
                filters = parsed["filters"]
                recs = agent_engine.get_recommendations(master_df, smart_recs, filters)
                if recs:
                    top_pref = any(r.get("is_tbo_preferred") for r in recs)
                    boost_note = "⭐ **Prioritized TBO Smart Buying inventory** with guaranteed instant confirmation is shown at the top!" if top_pref else ""
                    reply_text = (
                        f"Found **{len(recs)} top hotel matches** matching your criteria:\n"
                        f"{boost_note}\n\n"
                        f"Click **Select for Booking** on any card or use the form on the right to reserve."
                    )
                else:
                    reply_text = "No exact matches found for your filter criteria. Try relaxing your budget or searching for Palm Jumeirah or Downtown Dubai."
                    recs = []

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": reply_text,
                    "recommendations": recs
                })
                st.rerun()

    # Right Column: Booking Creation & Strict Cancellation Workflow
    with col_manage:
        st.markdown("### 📝 Instant Booking & Confirmation")
        
        # Booking form
        with st.expander("⚡ Make a Simulated Booking", expanded=True):
            # Find candidate hotels to book
            hotel_names = list(master_df["canonical_name"].unique())
            
            # Pre-selection sync with chat selections
            default_idx = 0
            if "selected_booking_hotel" in st.session_state and st.session_state.selected_booking_hotel in hotel_names:
                default_idx = hotel_names.index(st.session_state.selected_booking_hotel)

            selected_h_name = st.selectbox("Choose Hotel to Book:", hotel_names, index=default_idx, key="book_hotel_name")
            
            # Lookup hotel record & smart buying status
            h_data = master_df[master_df["canonical_name"] == selected_h_name].iloc[0]
            proc_match = smart_recs[smart_recs["master_hotel_id"] == h_data["master_hotel_id"]]
            is_proc = False
            avail_rooms = 0
            selling_price = round(h_data["best_price_inr"] * 1.20, -2)
            
            if not proc_match.empty:
                is_proc = (proc_match.iloc[0]["status"] == "Purchased")
                avail_rooms = int(proc_match.iloc[0]["available_rooms"])
                selling_price = proc_match.iloc[0]["suggested_selling_price"]

            if is_proc:
                st.markdown(f"<span class='badge-procured'>⭐ TBO Strategic Inventory — {avail_rooms} rooms in stock</span>", unsafe_allow_html=True)
            else:
                st.caption(f"Standard Catalog Fulfillment via {h_data['best_supplier']}")

            guest_name = st.text_input("Lead Guest Name:", value="Rahul Sharma")
            b_c1, b_c2 = st.columns(2)
            with b_c1:
                check_in_date = st.date_input("Check-In Date:", value=date.today() + timedelta(days=7))
            with b_c2:
                check_out_date = st.date_input("Check-Out Date:", value=date.today() + timedelta(days=10))

            num_guests = st.number_input("Guests:", min_value=1, max_value=6, value=2)
            rooms_count = st.number_input("Rooms:", min_value=1, max_value=5, value=1)
            
            nights = max(1, (check_out_date - check_in_date).days)
            total_est = selling_price * nights * rooms_count
            st.markdown(f"**Total Price:** `₹{total_est:,.0f}` ({nights} nights @ ₹{selling_price:,.0f}/night)")

            if st.button("Confirm Simulated Booking", type="primary"):
                hotel_payload = {
                    "master_hotel_id": h_data["master_hotel_id"],
                    "canonical_name": h_data["canonical_name"],
                    "area": h_data["area"],
                    "selling_price": selling_price,
                    "best_supplier": h_data["best_supplier"],
                    "meals": h_data["best_meals"],
                    "cancellation_policy": h_data["best_cancellation"],
                    "room_type": h_data["best_room_type"],
                    "is_tbo_preferred": is_proc
                }
                new_b = add_new_booking(
                    hotel_data=hotel_payload,
                    guest_name=guest_name,
                    check_in=str(check_in_date),
                    check_out=str(check_out_date),
                    num_guests=num_guests,
                    rooms=rooms_count
                )
                st.success(f"🎉 Booking Confirmed! ID: **{new_b['booking_id']}**")
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"🎉 **Booking Confirmed!**\n\n• **Booking ID:** `{new_b['booking_id']}`\n• **Hotel:** {new_b['hotel_name']}\n• **Guest:** {new_b['guest_name']}\n• **Dates:** {new_b['check_in']} to {new_b['check_out']} ({new_b['nights']} nights)\n• **Total Paid:** ₹{new_b['total_amount']:,.0f}\n• **Inventory Updated:** Deducted {new_b['rooms']} room(s) from Smart Buying stock."
                })
                st.rerun()

        # Strict Cancellation Confirmation Workflow
        st.markdown("#### 🛡️ Booking Management & Cancellation")
        
        # Check if cancellation was initiated
        if st.session_state.pending_cancellation_id:
            pend_id = st.session_state.pending_cancellation_id
            target_booking = next((b for b in st.session_state.bookings if b["booking_id"] == pend_id), None)
            
            if target_booking and target_booking["status"] == "CONFIRMED":
                alert_box_html = (
                    f'<div class="alert-box">'
                    f'<h4 style="margin: 0 0 6px 0; color: #B45309;">⚠️ Cancellation Confirmation Required</h4>'
                    f'<p style="margin: 4px 0;">Please review the booking details before confirming cancellation:</p>'
                    f'<ul style="margin: 4px 0; padding-left: 18px;">'
                    f'<li><b>Booking ID:</b> {target_booking["booking_id"]}</li>'
                    f'<li><b>Hotel:</b> {target_booking["hotel_name"]} ({target_booking["area"]})</li>'
                    f'<li><b>Guest:</b> {target_booking["guest_name"]}</li>'
                    f'<li><b>Stay:</b> {target_booking["check_in"]} to {target_booking["check_out"]} ({target_booking["nights"]} nights)</li>'
                    f'<li><b>Amount:</b> ₹{target_booking["total_amount"]:,.0f}</li>'
                    f'<li><b>Policy:</b> {target_booking["cancellation_policy"]}</li>'
                    f'</ul>'
                    f'<p style="margin: 6px 0 0 0; font-size: 12px; color: #92400E;"><b>Note:</b> Confirming will cancel this reservation and restore room inventory back to Smart Buying.</p>'
                    f'</div>'
                )
                st.markdown(alert_box_html, unsafe_allow_html=True)
                
                can_col1, can_col2 = st.columns(2)
                with can_col1:
                    if st.button("✓ Confirm Cancellation", type="primary", key="btn_confirm_cancel"):
                        execute_cancellation(pend_id)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": f"✅ **Booking Cancelled:** `{pend_id}` for {target_booking['hotel_name']} has been cancelled. Inventory restored to Smart Buying."
                        })
                        st.success(f"Booking {pend_id} cancelled.")
                        st.rerun()
                with can_col2:
                    if st.button("✕ Keep Booking", key="btn_keep_booking"):
                        st.session_state.pending_cancellation_id = None
                        st.info("Cancellation aborted. Booking remains active.")
                        st.rerun()
            else:
                st.session_state.pending_cancellation_id = None

        # Active Bookings List
        bookings = st.session_state.bookings
        if bookings:
            for b in reversed(bookings):
                is_conf = (b["status"] == "CONFIRMED")
                status_color = "#16A34A" if is_conf else "#DC2626"
                
                b_card_html = (
                    f'<div style="border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 8px; background: white;">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                    f'<span style="font-weight: 700; color: #0F172A;">{b["booking_id"]}</span>'
                    f'<span style="color: {status_color}; font-weight: 600; font-size: 12px;">{b["status"]}</span>'
                    f'</div>'
                    f'<div style="font-size: 13px; color: #1E293B; margin: 4px 0;"><b>{b["hotel_name"]}</b> ({b["nights"]} nights)</div>'
                    f'<div style="font-size: 11px; color: #64748B;">Guest: {b["guest_name"]} | ₹{b["total_amount"]:,.0f} total</div>'
                    f'</div>'
                )
                st.markdown(b_card_html, unsafe_allow_html=True)
                
                if is_conf:
                    if st.button(f"Cancel {b['booking_id']}", key=f"cancel_btn_{b['booking_id']}"):
                        st.session_state.pending_cancellation_id = b["booking_id"]
                        st.rerun()
        else:
            st.caption("No bookings created yet. Use the form above or chat to simulate your first booking.")
