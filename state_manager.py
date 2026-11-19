"""
state_manager.py - Centralized State & Workflow Synchronization
Integrates all three modules:
Supplier Data -> Clean Catalog -> Smart Buying -> AI Travel Agent -> Booking Data -> Demand Updates
Maintains synchronized records across Streamlit session runs.
"""

import streamlit as st
import pandas as pd
from data_generator import generate_raw_supplier_listings, generate_historical_demand
from catalog_cleaner import clean_and_merge_catalog
from smart_buyer import compute_demand_forecast, optimize_purchasing
from travel_agent import TravelAgentEngine

DEFAULT_BUDGET = 5000000.0  # ₹50,00,000 (₹50 Lakhs)

def initialize_system_state():
    """Initializes all data structures in st.session_state if not already present."""
    if "agent_engine" not in st.session_state:
        st.session_state.agent_engine = TravelAgentEngine()

    if "raw_listings" not in st.session_state:
        st.session_state.raw_listings = generate_raw_supplier_listings()

    if "catalog_cleaned" not in st.session_state or not st.session_state.catalog_cleaned:
        run_catalog_cleaning()

    if "purchasing_budget" not in st.session_state:
        st.session_state.purchasing_budget = DEFAULT_BUDGET

    if "smart_buying_done" not in st.session_state or not st.session_state.smart_buying_done:
        run_smart_buying(st.session_state.purchasing_budget)

    if "bookings" not in st.session_state:
        st.session_state.bookings = []

    if "pending_cancellation_id" not in st.session_state:
        st.session_state.pending_cancellation_id = None

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Hello! I'm your TBO AI Travel Assistant.**\n\n"
                    "I search our verified, cleaned catalog and prioritize our exclusive "
                    "**Smart Buying inventory** with guaranteed best B2B rates.\n\n"
                    "Tell me your travel preferences (e.g. *'5-star in Palm Jumeirah with breakfast'*, "
                    "*'Budget hotel in Downtown under ₹15,000'*, or ask to view/cancel your bookings)!"
                )
            }
        ]

def run_catalog_cleaning(threshold: float = 65.0):
    """Executes RapidFuzz duplicate detection and catalog merging."""
    master_df, comps, pairs, metrics = clean_and_merge_catalog(
        st.session_state.raw_listings,
        similarity_threshold=threshold
    )
    st.session_state.master_catalog = master_df
    st.session_state.supplier_comparisons = comps
    st.session_state.pairwise_duplicates = pairs
    st.session_state.cleaning_metrics = metrics
    st.session_state.catalog_cleaned = True
    
    # Initialize / refresh demand data for the master catalog
    if "demand_history" not in st.session_state or st.session_state.demand_history is None:
        st.session_state.demand_history = generate_historical_demand(master_df)
    
    st.session_state.forecasted_demand = compute_demand_forecast(st.session_state.demand_history)

def run_smart_buying(budget: float):
    """Executes demand forecasting and budget optimization."""
    st.session_state.purchasing_budget = float(budget)
    recs, summary = optimize_purchasing(
        st.session_state.master_catalog,
        st.session_state.forecasted_demand,
        total_budget=float(budget)
    )
    # Deduct active confirmed bookings from newly optimized available_rooms
    if "bookings" in st.session_state and st.session_state.bookings:
        for b in st.session_state.bookings:
            if b.get("status") == "CONFIRMED":
                hid = b["master_hotel_id"]
                idx = recs.index[recs["master_hotel_id"] == hid].tolist()
                if idx and recs.loc[idx[0], "status"] == "Purchased":
                    recs.loc[idx[0], "available_rooms"] = max(
                        0, recs.loc[idx[0], "available_rooms"] - b["rooms"]
                    )

    st.session_state.procurement_recommendations = recs
    st.session_state.smart_buyer_summary = summary
    st.session_state.smart_buying_done = True

def add_new_booking(hotel_data: dict, guest_name: str, check_in: str, check_out: str, num_guests: int = 2, rooms: int = 1):
    """
    Creates a simulated booking, deducts available Smart Buying inventory,
    and updates live demand records.
    Returns (booking_record, error_message). error_message is None on success.
    """
    engine = st.session_state.agent_engine
    hid = hotel_data["master_hotel_id"]
    rec_df = st.session_state.procurement_recommendations
    idx = rec_df.index[rec_df["master_hotel_id"] == hid].tolist()

    # --- Inventory availability guard ---
    # Only block when the hotel is a procured (Purchased) property with tracked stock.
    # Standard catalog hotels are fulfilled on-demand without a stock limit.
    if idx:
        row_status = rec_df.loc[idx[0], "status"]
        curr_avail = int(rec_df.loc[idx[0], "available_rooms"])
        if row_status == "Purchased" and curr_avail < rooms:
            # Return a sentinel booking with status INVENTORY_UNAVAILABLE so the caller can surface a warning.
            error_booking = {
                "booking_id": None,
                "hotel_name": hotel_data["canonical_name"],
                "status": "INVENTORY_UNAVAILABLE",
                "error": (
                    f"Insufficient inventory: only {curr_avail} room(s) available for "
                    f"{hotel_data['canonical_name']} but {rooms} requested."
                )
            }
            return error_booking

    booking = engine.create_booking(
        hotel_data=hotel_data,
        guest_name=guest_name,
        check_in=check_in,
        check_out=check_out,
        num_guests=num_guests,
        rooms=rooms
    )
    st.session_state.bookings.append(booking)

    # Deduct room inventory in Smart Buying recommendations
    if idx:
        curr_avail = rec_df.loc[idx[0], "available_rooms"]
        rec_df.loc[idx[0], "available_rooms"] = max(0, curr_avail - rooms)
        st.session_state.procurement_recommendations = rec_df

    # Increment live demand in demand_history
    d_df = st.session_state.demand_history
    d_idx = d_df.index[d_df["master_hotel_id"] == hid].tolist()
    if d_idx:
        d_df.loc[d_idx[0], "week_8"] += rooms
        d_df.loc[d_idx[0], "last_week_demand"] += rooms
        st.session_state.demand_history = d_df
        # Re-run demand forecast dynamically
        st.session_state.forecasted_demand = compute_demand_forecast(d_df)

    return booking

def execute_cancellation(booking_id: str):
    """
    Executes explicit confirmed cancellation:
    Updates booking status to CANCELLED, restores Smart Buying inventory,
    and adjusts demand information.
    """
    found = False
    for b in st.session_state.bookings:
        if b["booking_id"] == booking_id and b["status"] == "CONFIRMED":
            b["status"] = "CANCELLED"
            found = True
            hid = b["master_hotel_id"]
            rooms = b["rooms"]

            # Restore Smart Buying inventory room count up to allocated block limit
            rec_df = st.session_state.procurement_recommendations
            idx = rec_df.index[rec_df["master_hotel_id"] == hid].tolist()
            if idx and rec_df.loc[idx[0], "status"] == "Purchased":
                rec_df.loc[idx[0], "available_rooms"] = min(
                    rec_df.loc[idx[0], "rooms_to_purchase"],
                    rec_df.loc[idx[0], "available_rooms"] + rooms
                )
                st.session_state.procurement_recommendations = rec_df

            # Adjust demand: reverse the booking-time increments on week_8 and last_week_demand
            d_df = st.session_state.demand_history
            d_idx = d_df.index[d_df["master_hotel_id"] == hid].tolist()
            if d_idx:
                d_df.loc[d_idx[0], "week_8"] = max(0, d_df.loc[d_idx[0], "week_8"] - rooms)
                d_df.loc[d_idx[0], "last_week_demand"] = max(0, d_df.loc[d_idx[0], "last_week_demand"] - rooms)
                st.session_state.demand_history = d_df
                st.session_state.forecasted_demand = compute_demand_forecast(d_df)
            break
            
    st.session_state.pending_cancellation_id = None
    return found

def get_pipeline_integration_metrics():
    """Calculates end-to-end integration metrics directly from shared application state."""
    raw_total = len(st.session_state.raw_listings)
    unique_master = len(st.session_state.master_catalog)
    dup_detected = st.session_state.cleaning_metrics["duplicates_identified"]
    dup_reduction_pct = st.session_state.cleaning_metrics["duplicate_reduction_pct"]
    
    budget = float(st.session_state.purchasing_budget)
    rec_df = st.session_state.procurement_recommendations
    
    # Calculate directly from live procurement records
    purchased_mask = rec_df["status"] == "Purchased"
    procured_hotels = int(purchased_mask.sum())
    total_procured_rooms = int(rec_df["rooms_to_purchase"].sum())
    available_procured_rooms = int(rec_df["available_rooms"].sum())
    allocated_investment = float(rec_df["total_investment"].sum())
    projected_profit = float(rec_df["expected_profit"].sum())
    budget_utilization_pct = round((allocated_investment / budget) * 100, 1) if budget > 0 else 0.0
    blended_roi_pct = round((projected_profit / allocated_investment) * 100, 1) if allocated_investment > 0 else 0.0
    
    # Live bookings
    bookings = st.session_state.bookings
    confirmed_bookings = [b for b in bookings if b.get("status") == "CONFIRMED"]
    cancelled_bookings = [b for b in bookings if b.get("status") == "CANCELLED"]
    
    live_revenue_realized = sum(b.get("total_amount", 0) for b in confirmed_bookings)
    rooms_sold_live = sum(b.get("rooms", 0) for b in confirmed_bookings)
    
    return {
        "raw_total": raw_total,
        "unique_master": unique_master,
        "duplicates_identified": dup_detected,
        "duplicate_reduction_pct": dup_reduction_pct,
        "budget": budget,
        "allocated_investment": allocated_investment,
        "procured_hotels": procured_hotels,
        "total_procured_rooms": total_procured_rooms,
        "available_procured_rooms": available_procured_rooms,
        "projected_profit": projected_profit,
        "budget_utilization_pct": budget_utilization_pct,
        "blended_roi_pct": blended_roi_pct,
        "total_bookings_count": len(bookings),
        "confirmed_bookings_count": len(confirmed_bookings),
        "cancelled_bookings_count": len(cancelled_bookings),
        "live_revenue_realized": live_revenue_realized,
        "rooms_sold_live": rooms_sold_live
    }
