"""
travel_agent.py - Conversational AI Travel Agent with Smart Buying Integration
Handles natural queries for Dubai hotels, prioritizes Smart Buying inventory,
creates instant simulated bookings (deducting procured rooms & updating demand),
and strictly enforces a 2-step confirmation workflow for cancellations.
"""

import re
import random
from datetime import datetime, timedelta
import pandas as pd

class TravelAgentEngine:
    def __init__(self):
        pass

    def parse_user_intent(self, user_msg: str):
        """
        Extracts travel dates, budget, guest count, location preferences, and intent
        from user conversational input.
        """
        msg_lower = user_msg.lower()
        
        # Check for cancellation intent.
        # Rule: only treat the message as a cancellation REQUEST when the user is
        # explicitly acting to cancel their own booking.  Positive signals:
        #   (a) A TBO-DXB-XXXXX booking ID appears anywhere in the message, OR
        #   (b) The phrasing is an action verb directed at a booking/reservation
        #       e.g. 'cancel my booking', 'I want to cancel', 'cancel booking TBO-...'
        # Negative guard: phrases like 'free cancellation', 'free cancel policy',
        # or 'cancellation policy' describe a *hotel feature* the user wants to
        # search for, so they must fall through to the recommend intent.
        _has_booking_id = bool(re.search(r'tbo-dxb-\d{5}', msg_lower))
        _action_cancel  = bool(re.search(
            r'(?:i\s+(?:want|need|would like)\s+to\s+cancel'
            r'|cancel\s+(?:my|this|the)\s+(?:booking|reservation|trip)'
            r'|cancel\s+booking'
            r'|cancel\s+reservation)',
            msg_lower
        ))
        # 'free cancellation' / 'free cancel' / 'cancellation policy' = hotel policy preference
        _policy_phrase  = bool(re.search(r'free\s*cancel|cancellation\s+polic', msg_lower))

        if (_has_booking_id or _action_cancel) and not _policy_phrase:
            booking_id = None
            raw_id = re.search(r'tbo-dxb-\d{5}', msg_lower)
            if raw_id:
                booking_id = raw_id.group(0).upper()
            return {"intent": "cancel_request", "booking_id": booking_id}

# Check for viewing bookings
        if any(w in msg_lower for w in ["my booking", "view booking", "show booking", "current booking", "active booking", "list booking"]):
            return {"intent": "view_bookings"}

        # Check for direct booking intent
        book_match = re.search(r'(?:book|reserve)\s+(htl-\d{3}|[a-zA-Z\s]+)', msg_lower)
        if "book" in msg_lower and any(w in msg_lower for w in ["htl-", "hotel", "room", "stay", "atlantis", "rove", "marriott", "palace"]):
            hotel_id_match = re.search(r'htl-\d{3}', msg_lower)
            hotel_ref = hotel_id_match.group(0).upper() if hotel_id_match else None
            return {"intent": "book_request", "hotel_ref": hotel_ref}

        # Query / Recommendation Intent
        filters = {
            "area": None,
            "max_price": None,
            "min_rating": None,
            "meals": None,
            "free_cancel": False,
            "luxury": False,
            "guests": 2,
            "nights": 3
        }

        # Area matching
        area_keywords = {
            "palm": "Palm Jumeirah",
            "downtown": "Downtown Dubai",
            "marina": "Dubai Marina",
            "business bay": "Business Bay",
            "jbr": "JBR (Jumeirah Beach Residence)",
            "beach": "Palm Jumeirah",
            "barsha": "Al Barsha",
            "deira": "Deira / Creek",
            "creek": "Deira / Creek"
        }
        for kw, canonical_area in area_keywords.items():
            if kw in msg_lower:
                filters["area"] = canonical_area
                break

        # Budget matching (e.g. "under 15000", "budget 20000", "below 10k", "< 25000")
        budget_match = re.search(r'(?:under|below|less than|budget of|within|max|<|<=)\s*(?:inr|rs\.?|₹)?\s*(\d+)(?:k)?', msg_lower)
        if budget_match:
            val = int(budget_match.group(1))
            if "k" in msg_lower[budget_match.start():budget_match.end() + 2]:
                val *= 1000
            elif val < 100:  # e.g. "20k"
                val *= 1000
            filters["max_price"] = val

        # Guest count
        guest_match = re.search(r'(\d+)\s*(?:guest|people|person|adult)', msg_lower)
        if guest_match:
            filters["guests"] = int(guest_match.group(1))

        # Nights count
        night_match = re.search(r'(\d+)\s*(?:night|day)', msg_lower)
        if night_match:
            filters["nights"] = int(night_match.group(1))

        # Amenities / Preferences
        if "breakfast" in msg_lower:
            filters["meals"] = "Breakfast Included"
        if "free cancel" in msg_lower or "refundable" in msg_lower:
            filters["free_cancel"] = True
        if "luxury" in msg_lower or "5 star" in msg_lower or "5-star" in msg_lower or "high-end" in msg_lower:
            filters["luxury"] = True
            filters["min_rating"] = 4.5

        return {"intent": "recommend", "filters": filters}

    def get_recommendations(self, master_df: pd.DataFrame, smart_buyer_recs: pd.DataFrame, filters: dict, top_k: int = 4):
        """
        Filters and ranks hotels using cleaned catalog and Smart Buying inventory priority.
        Smart Buying procured inventory with available rooms gets priority boost.
        """
        # Map procurement data
        procured_map = {}
        if smart_buyer_recs is not None and not smart_buyer_recs.empty:
            for _, r in smart_buyer_recs.iterrows():
                procured_map[r["master_hotel_id"]] = {
                    "status": r.get("status", "Excluded (Budget Cap)"),
                    "procured": r.get("status") == "Purchased",
                    "available_rooms": r.get("available_rooms", 0),
                    "suggested_selling_price": r.get("suggested_selling_price", r.get("procurement_cost_unit", 10000)),
                    "total_purchased_rooms": r.get("rooms_to_purchase", 0)
                }

        results = []
        for _, h in master_df.iterrows():
            hid = h["master_hotel_id"]
            p_info = procured_map.get(hid, {
                "procured": False,
                "available_rooms": 0,
                "suggested_selling_price": round(h["best_price_inr"] * 1.20, -2)
            })
            
            selling_price = p_info["suggested_selling_price"]
            
            # Apply filters
            if filters.get("area") and filters["area"] != h["area"]:
                continue
            if filters.get("max_price") and selling_price > filters["max_price"]:
                continue
            if filters.get("min_rating") and h["rating"] < filters["min_rating"]:
                continue
            if filters.get("meals") and not h.get("has_breakfast", False):
                continue
            if filters.get("free_cancel") and not h.get("has_free_cancel", False):
                continue
            if filters.get("luxury") and h["rating"] < 4.5:
                continue

            # Prioritization scoring:
            # Procured hotels with stock get a massive 50-point boost!
            is_procured = p_info["procured"] and p_info["available_rooms"] > 0
            base_score = h["rank_score"]
            priority_score = base_score + (50.0 if is_procured else 0.0)

            results.append({
                "master_hotel_id": hid,
                "canonical_name": h["canonical_name"],
                "area": h["area"],
                "rating": h["rating"],
                "selling_price": selling_price,
                "original_supplier_price": h["best_price_inr"],
                "best_supplier": h["best_supplier"],
                "meals": h["best_meals"],
                "cancellation_policy": h["best_cancellation"],
                "room_type": h["best_room_type"],
                "description": h["description"],
                "is_tbo_preferred": is_procured,
                "available_rooms": p_info["available_rooms"],
                "priority_score": priority_score
            })

        # Sort by priority score
        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values(by="priority_score", ascending=False).head(top_k)
            return results_df.to_dict(orient="records")
        return []

    def create_booking(self, hotel_data: dict, guest_name: str, check_in: str, check_out: str, num_guests: int = 2, rooms: int = 1):
        """
        Simulates booking creation, returns a structured booking confirmation record.
        """
        booking_id = f"TBO-DXB-{random.randint(10000, 99999)}"
        
        # Calculate nights
        try:
            d_in = datetime.strptime(check_in, "%Y-%m-%d")
            d_out = datetime.strptime(check_out, "%Y-%m-%d")
            nights = max(1, (d_out - d_in).days)
        except Exception:
            nights = 3
            
        rate_per_night = hotel_data["selling_price"]
        total_amount = rate_per_night * nights * rooms
        
        booking_record = {
            "booking_id": booking_id,
            "master_hotel_id": hotel_data["master_hotel_id"],
            "hotel_name": hotel_data["canonical_name"],
            "area": hotel_data["area"],
            "guest_name": guest_name,
            "num_guests": num_guests,
            "rooms": rooms,
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "rate_per_night": rate_per_night,
            "total_amount": total_amount,
            "supplier": hotel_data["best_supplier"],
            "meals": hotel_data["meals"],
            "cancellation_policy": hotel_data["cancellation_policy"],
            "room_type": hotel_data["room_type"],
            "is_tbo_preferred": hotel_data.get("is_tbo_preferred", False),
            "status": "CONFIRMED",
            "booking_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return booking_record
