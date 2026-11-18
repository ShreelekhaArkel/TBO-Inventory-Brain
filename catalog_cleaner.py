"""
catalog_cleaner.py - Duplicate Detection, Merging, and Multi-Factor Ranking
Uses RapidFuzz to detect equivalent hotel listings across suppliers, merges them
into master records while preserving supplier-level differences, computes match
confidence scores, and ranks canonical hotels.
"""

import pandas as pd
import numpy as np
from rapidfuzz import fuzz

LOCATION_STOP_WORDS = {
    "dubai", "palm", "jumeirah", "downtown", "marina", "barsha", "al barsha",
    "deira", "creek", "jaddaf", "al jaddaf", "business bay", "jbr", "burj", "khalifa", "city"
}

GENERIC_HOTEL_WORDS = {
    "hotel", "resorts", "resort", "suites", "suite", "the", "&", "and", "spa",
    "apartments", "luxury collection", "luxury", "international", "group"
}

def clean_and_extract_brand(text: str):
    """Cleans hotel name and extracts core distinctive brand tokens."""
    if not isinstance(text, str):
        return "", set()
    cleaned = text.lower()
    for w in GENERIC_HOTEL_WORDS:
        cleaned = cleaned.replace(f" {w} ", " ").replace(f" {w}", "").replace(f"{w} ", "")
    cleaned = "".join(c if c.isalnum() or c.isspace() else " " for c in cleaned)
    tokens = set(cleaned.split())
    core_tokens = {w for w in tokens if w not in LOCATION_STOP_WORDS}
    return " ".join(cleaned.split()), core_tokens

def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Computes brand-aware name similarity:
    - Isolates distinctive brand names from geographic landmarks
    - Evaluates token sort ratio and brand token overlap
    """
    cleaned1, core1 = clean_and_extract_brand(name1)
    cleaned2, core2 = clean_and_extract_brand(name2)
    
    sort_ratio = fuzz.token_sort_ratio(cleaned1, cleaned2)
    
    if core1 and core2:
        overlap = core1.intersection(core2)
        if overlap:
            frac = len(overlap) / max(len(core1), len(core2))
            if frac >= 0.5:
                core_sort = fuzz.token_sort_ratio(" ".join(sorted(core1)), " ".join(sorted(core2)))
                return max(sort_ratio, core_sort)
        else:
            # Different brand names entirely (e.g. Atlantis vs Sofitel, both on Palm)
            return min(sort_ratio, 35.0)
            
    return sort_ratio

def calculate_listing_similarity(row1, row2):
    """
    Computes composite similarity score between two listings based on:
    - Hotel Name (55% weight)
    - Location / Address (30% weight)
    - Description (15% weight)
    """
    name_sim = calculate_name_similarity(row1["hotel_name"], row2["hotel_name"])
    
    loc_sim = fuzz.token_set_ratio(str(row1["location"]), str(row2["location"]))
    desc_sim = fuzz.token_set_ratio(str(row1["description"]), str(row2["description"]))

    composite = (0.55 * name_sim) + (0.30 * loc_sim) + (0.15 * desc_sim)
    return {
        "composite_score": round(composite, 2),
        "name_sim": round(name_sim, 2),
        "loc_sim": round(loc_sim, 2),
        "desc_sim": round(desc_sim, 2)
    }

def clean_and_merge_catalog(raw_df: pd.DataFrame, similarity_threshold: float = 65.0):
    """
    Runs duplicate detection across raw listings using RapidFuzz, merges equivalent
    listings into master records, calculates matching confidence, and ranks hotels.
    """
    n = len(raw_df)
    adj = {i: set() for i in range(n)}
    pairwise_matches = []

    # 1. Pairwise comparison
    for i in range(n):
        for j in range(i + 1, n):
            row_i = raw_df.iloc[i]
            row_j = raw_df.iloc[j]
            
            sim_dict = calculate_listing_similarity(row_i, row_j)
            composite = sim_dict["composite_score"]
            name_sim = sim_dict["name_sim"]
            loc_sim = sim_dict["loc_sim"]
            
            # Match condition: brand name match >= 65% AND (same area OR loc_sim >= 50%) AND composite >= 65%
            is_match = False
            if name_sim >= 65.0 and (row_i["area"] == row_j["area"] or loc_sim >= 50.0) and composite >= similarity_threshold:
                is_match = True

            if is_match:
                adj[i].add(j)
                adj[j].add(i)
                pairwise_matches.append({
                    "listing_id_1": row_i["listing_id"],
                    "hotel_1": row_i["hotel_name"],
                    "supplier_1": row_i["supplier"],
                    "price_1": row_i["price_inr"],
                    "listing_id_2": row_j["listing_id"],
                    "hotel_2": row_j["hotel_name"],
                    "supplier_2": row_j["supplier"],
                    "price_2": row_j["price_inr"],
                    "name_similarity": name_sim,
                    "location_similarity": loc_sim,
                    "description_similarity": sim_dict["desc_sim"],
                    "confidence_score": composite
                })

    # 2. Connected components clustering
    visited = set()
    clusters = []
    for i in range(n):
        if i not in visited:
            cluster = []
            queue = [i]
            visited.add(i)
            while queue:
                curr = queue.pop(0)
                cluster.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            clusters.append(cluster)

    # 3. Build Master Hotel Records
    master_records = []
    supplier_comparisons = {}
    
    min_catalog_price = raw_df["price_inr"].min()
    max_catalog_price = raw_df["price_inr"].max()

    for idx, cluster_indices in enumerate(clusters):
        cluster_rows = raw_df.iloc[cluster_indices]
        master_id = f"HTL-{idx+1:03d}"

        # Determine canonical name from the most reliable supplier or cleanest entry
        sorted_by_rel = cluster_rows.sort_values(by="supplier_reliability", ascending=False)
        canonical_name = sorted_by_rel.iloc[0]["_true_canonical_name"] if "_true_canonical_name" in cluster_rows.columns else sorted_by_rel.iloc[0]["hotel_name"]
        canonical_area = cluster_rows["area"].mode().iloc[0]
        avg_rating = round(cluster_rows["rating"].mean(), 1)

        # Supplier comparisons
        offers = []
        for _, r in cluster_rows.iterrows():
            offers.append({
                "listing_id": r["listing_id"],
                "supplier": r["supplier"],
                "supplier_reliability": r["supplier_reliability"],
                "price_inr": r["price_inr"],
                "rating": r["rating"],
                "meals": r["meals"],
                "cancellation_policy": r["cancellation_policy"],
                "room_type": r["room_type"],
                "raw_name": r["hotel_name"]
            })

        # Find best offer (lowest price, highest reliability on tie)
        offers_sorted = sorted(offers, key=lambda x: (x["price_inr"], -x["supplier_reliability"]))
        best_offer = offers_sorted[0]
        
        # Calculate cluster match confidence score
        if len(cluster_indices) > 1:
            cluster_pair_scores = [
                m["confidence_score"] for m in pairwise_matches
                if m["listing_id_1"] in cluster_rows["listing_id"].values and m["listing_id_2"] in cluster_rows["listing_id"].values
            ]
            avg_confidence = round(float(np.mean(cluster_pair_scores)), 1) if cluster_pair_scores else 90.0
        else:
            avg_confidence = 100.0

        # Price spread & savings
        prices = [o["price_inr"] for o in offers]
        min_p = min(prices)
        max_p = max(prices)
        spread = max_p - min_p
        savings_pct = round((spread / max_p) * 100, 1) if max_p > 0 else 0.0

        # Multi-factor Hotel Rank Score (0 - 100):
        # 1. Rating (40 pts)
        rating_score = (avg_rating / 5.0) * 40
        # 2. Price competitiveness (30 pts)
        norm_price = (min_p - min_catalog_price) / (max_catalog_price - min_catalog_price + 1e-5)
        price_score = (1.0 - norm_price) * 30
        # 3. Supplier reliability (20 pts)
        rel_score = best_offer["supplier_reliability"] * 20
        # 4. Supplier redundancy / offer density (10 pts)
        density_score = min(len(offers) / 3.0, 1.0) * 10

        composite_rank = round(rating_score + price_score + rel_score + density_score, 1)

        # Check availability of amenities across all supplier offers
        has_breakfast = any("breakfast" in str(o["meals"]).lower() or "half board" in str(o["meals"]).lower() for o in offers)
        has_free_cancel = any("free cancellation" in str(o["cancellation_policy"]).lower() for o in offers)

        master_record = {
            "master_hotel_id": master_id,
            "canonical_name": canonical_name,
            "area": canonical_area,
            "rating": avg_rating,
            "best_price_inr": min_p,
            "max_price_inr": max_p,
            "supplier_savings_inr": spread,
            "savings_pct": savings_pct,
            "best_supplier": best_offer["supplier"],
            "best_supplier_reliability": best_offer["supplier_reliability"],
            "best_meals": best_offer["meals"],
            "best_cancellation": best_offer["cancellation_policy"],
            "has_breakfast": has_breakfast,
            "has_free_cancel": has_free_cancel,
            "best_room_type": best_offer["room_type"],
            "supplier_count": len(offers),
            "match_confidence": avg_confidence,
            "rank_score": composite_rank,
            "description": sorted_by_rel.iloc[0]["description"],
            "raw_listing_ids": list(cluster_rows["listing_id"].values)
        }
        master_records.append(master_record)
        supplier_comparisons[master_id] = offers

    master_df = pd.DataFrame(master_records).sort_values(by="rank_score", ascending=False).reset_index(drop=True)

    # 4. Summary metrics
    total_raw = len(raw_df)
    unique_master = len(master_df)
    duplicates_detected = total_raw - unique_master
    reduction_pct = round((duplicates_detected / total_raw) * 100, 1)

    metrics = {
        "total_raw_listings": total_raw,
        "unique_hotels": unique_master,
        "duplicates_identified": duplicates_detected,
        "duplicate_reduction_pct": reduction_pct
    }

    pairwise_df = pd.DataFrame(pairwise_matches)
    return master_df, supplier_comparisons, pairwise_df, metrics

if __name__ == "__main__":
    from data_generator import generate_raw_supplier_listings
    raw = generate_raw_supplier_listings()
    master, comps, pairs, m = clean_and_merge_catalog(raw)
    print("Catalog Cleaner Validation:")
    print("Metrics:", m)
    print("Master Hotels count:", len(master))
    print(master[["master_hotel_id", "canonical_name", "area", "best_price_inr", "best_supplier", "rank_score", "match_confidence"]].to_string())
