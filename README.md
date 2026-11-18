# TBO Inventory Brain – Hackathon Prototype

**"Clean the inventory, buy the right inventory, and sell it through an AI travel agent."**

A functional, integrated prototype demonstrating the full B2B travel distribution lifecycle for **Dubai Hotels**:
1. **Clean Catalog:** Multi-supplier ingestion, RapidFuzz duplicate detection, canonical record merging, and multi-factor hotel ranking.
2. **Smart Buying:** Weekly demand forecasting, budget-constrained procurement optimization (Knapsack), and -20% demand risk stress testing.
3. **AI Travel Agent:** Conversational hotel recommendation assistant with Smart Buying inventory priority boosting, simulated bookings, and strict 2-step cancellation confirmation.

---

## 🔄 End-to-End Integrated Architecture

All three modules share the same live state:

```
Supplier Ingestion (43 raw listings from 3 suppliers)
   │
   ▼
Clean Catalog (RapidFuzz deduplication: 43 raw -> 20 clean hotels, 53.5% reduction)
   │
   ▼
Smart Buying (Knapsack procurement under ₹50L budget, 20% markup, -20% downside stress test)
   │
   ▼
AI Travel Agent (Customer search prioritizes TBO Smart Buying inventory with instant guarantee)
   │
   ▼
Booking & Cancellation Feedback Loop (Deducts room stock on booking; restores stock on confirmed cancellation)
```

---

## 🚀 Quickstart & How to Run

### 1. Prerequisites
- Python 3.10+
- Installed packages: `streamlit`, `pandas`, `rapidfuzz`, `plotly`, `numpy`

### 2. Run the Application
Launch the Streamlit web dashboard:

```bash
python -m streamlit run app.py
```

The web dashboard opens at `http://localhost:8501`.

### 3. Run Automated Integration Tests
Verify all 8 demo workflow steps programmatically:

```bash
python test_integration.py
```

---

## 🎯 Hackathon Demo Workflow Guide

### Step 1: Clean Catalog & Deduplication
- Open the **Clean Catalog** tab.
- Inspect the **Raw Supplier Feed**: View 43 listings with brand variations, naming discrepancies, and price differences across *DirectBed Global*, *GulfTravel Wholesale*, and *OasisRooms B2B*.
- Review the **Cleaned Master Catalog**: 20 canonical Dubai properties, with 23 duplicates identified (53.5% catalog noise reduction).
- Check the **Supplier Comparison View**: Select any hotel (e.g. *Atlantis The Palm* or *JW Marriott Marquis*) to see price arbitrage savings (up to 15-20% savings by booking via the optimal supplier).
- Explore **RapidFuzz Analytics**: Inspect string similarity breakdown across Brand Name, Location, and Description.

### Step 2: Smart Buying & Risk Simulation
- Navigate to the **Smart Buying** tab.
- Inspect the default **₹50,00,000 (₹50 Lakhs)** purchasing budget:
  - 12-13 key hotels procured (300 room-nights).
  - 99.5%+ budget utilization (strictly `<= ₹50,00,000`).
  - Expected Revenue: ~₹59.7 Lakhs.
  - Expected Profit: ~₹9.94 Lakhs (~20% ROI).
- **Edit Budget:** Change budget to ₹25 Lakhs or ₹75 Lakhs to watch hotel allocations and profit metrics recalculate dynamically.
- **-20% Demand Risk:** Review the stress test chart showing performance under a 20% market contraction.

### Step 3: AI Travel Agent & Inventory Prioritization
- Open the **AI Travel Agent** tab.
- Ask a natural query or click a quick prompt (e.g., *"Luxury hotel in Palm Jumeirah with breakfast"* or *"Hotel in Downtown Dubai under 20000"*).
- Notice that hotels procured by Smart Buying receive a top-priority boost with the badge: **⭐ TBO Strategic Inventory (Instant Guarantee)**.
- Price displayed is the TBO Smart Buying selling price.

### Step 4: Simulated Booking & Real-Time Feedback
- In the right-hand panel, select a hotel, dates, and guests, then click **Confirm Simulated Booking**.
- Receive an instant confirmation summary and unique Booking ID (e.g. `TBO-DXB-XXXXX`).
- Notice that available room stock for that hotel in Smart Buying decrements immediately, and hotel demand updates.

### Step 5: Explicit 2-Step Cancellation
- In chat, type `Cancel <Booking-ID>` or click **Cancel** next to the active booking.
- Assistant displays an **explicit confirmation alert** showing full booking details, cancellation policy, and warning.
- Click **Confirm Cancellation**:
  - Booking status transitions to `CANCELLED`.
  - Room stock is restored back to Smart Buying inventory.

### Step 6: Verify Overview Metrics
- Return to **Overview** to see live updated sales volume, confirmed bookings count, and system pipeline status.

---

## 📁 File Structure

- `app.py`: Streamlit entrypoint with sidebar navigation, Dark Navy theme, and interactive dashboards.
- `data_generator.py`: Synthetic dataset of 43 Dubai hotel listings across 3 suppliers + 8-week historical demand.
- `catalog_cleaner.py`: RapidFuzz duplicate detection, canonical clustering, supplier arbitrage, and composite ranking.
- `smart_buyer.py`: Moving-average demand forecasting, knapsack budget allocation, and -20% demand risk stress test.
- `travel_agent.py`: Conversational assistant engine, Smart Buying inventory boosting, booking generation, and cancellation state machine.
- `state_manager.py`: Centralized state management linking all modules into a shared data loop.
- `styles.py`: Custom CSS for modern SaaS layout, dark navy header, responsive cards, and clean badges.
- `test_integration.py`: End-to-end automated test suite verifying all 8 requirements.
