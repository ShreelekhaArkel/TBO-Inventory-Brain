"""
data_generator.py - Synthetic dataset generator for Dubai Hotel Inventory
Generates realistic raw supplier listings with intentional duplicates, typos,
varying prices, meal plans, and cancellation policies across 3 suppliers.
Also generates historical weekly demand data for each canonical hotel.
"""

import pandas as pd
import numpy as np

# Canonical list of 20 distinct hotels in Dubai with realistic variations across suppliers
HOTEL_TEMPLATES = [
    {
        "canonical_name": "Atlantis The Palm",
        "area": "Palm Jumeirah",
        "base_rating": 4.8,
        "base_price": 42000,
        "base_weekly_demand": 38,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Atlantis, The Palm",
                "location": "Crescent Rd, Palm Jumeirah, Dubai",
                "desc": "Iconic luxury resort on Palm Jumeirah with Aquaventure waterpark access, private beach, and aquarium view rooms.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Ocean King Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Atlantis The Palm Dubai",
                "location": "The Palm Jumeirah, Dubai",
                "desc": "World-renowned 5-star beachfront resort featuring Lost Chambers aquarium, signature dining, and family entertainment.",
                "price_multiplier": 1.05,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Non-Refundable",
                "room_type": "Palm Deluxe Room"
            },
            {
                "supplier": "OasisRooms B2B",
                "name": "Atlantis Palm Resort & Spa",
                "location": "Palm Jumeirah East Crescent, Dubai",
                "desc": "Premier oceanfront resort with pristine private beach, water park entry, and luxury ocean suites.",
                "price_multiplier": 0.95,
                "rating_offset": -0.1,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Imperial Club Room"
            }
        ]
    },
    {
        "canonical_name": "Burj Al Arab Jumeirah",
        "area": "Jumeirah Beach",
        "base_rating": 4.9,
        "base_price": 115000,
        "base_weekly_demand": 12,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Burj Al Arab Jumeirah",
                "location": "Jumeirah Beach Road, Umm Suqeim 3, Dubai",
                "desc": "Ultra-luxury sail-shaped all-suite hotel with private butler service, duplex suites, and panoramic Arabian Gulf views.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Moderate (7 days)",
                "room_type": "One-Bedroom Deluxe Suite"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Burj Al Arab Luxury Suites",
                "location": "Jumeirah St, Dubai",
                "desc": "Icon of global luxury with private infinity pool terrace, Rolls Royce chauffeur service, and Michelin dining.",
                "price_multiplier": 1.04,
                "rating_offset": 0.0,
                "meals": "Half Board",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Panoramic Suite"
            }
        ]
    },
    {
        "canonical_name": "JW Marriott Marquis Hotel Dubai",
        "area": "Business Bay",
        "base_rating": 4.6,
        "base_price": 18000,
        "base_weekly_demand": 45,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "JW Marriott Marquis Hotel Dubai",
                "location": "Sheikh Zayed Road, Business Bay, Dubai",
                "desc": "Twin-tower 5-star hotel in Business Bay with award-winning Saray spa, heated pool, and 12 dining venues.",
                "price_multiplier": 1.02,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Deluxe Guest Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "JW Marriott Marquis Dubai",
                "location": "Business Bay, Dubai",
                "desc": "Luxury twin towers featuring heated pool, tranquil spa, and fine dining options close to Dubai Canal.",
                "price_multiplier": 0.98,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Superior King Room"
            },
            {
                "supplier": "OasisRooms B2B",
                "name": "Marriott Marquis Hotel - Business Bay",
                "location": "Sheikh Zayed Rd, Business Bay Dubai",
                "desc": "Contemporary 5-star hotel near Dubai Mall with spacious executive suites and full business lounge access.",
                "price_multiplier": 1.06,
                "rating_offset": -0.1,
                "meals": "Half Board",
                "cancellation": "Non-Refundable",
                "room_type": "Executive Suite"
            }
        ]
    },
    {
        "canonical_name": "Address Downtown",
        "area": "Downtown Dubai",
        "base_rating": 4.8,
        "base_price": 35000,
        "base_weekly_demand": 34,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Address Downtown",
                "location": "Downtown Dubai, Near Dubai Mall",
                "desc": "Flagship luxury hotel directly facing Burj Khalifa and Dubai Fountain with direct air-conditioned mall bridge.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Fountain View Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "The Address Hotel Downtown Dubai",
                "location": "Sheikh Mohammed bin Rashid Blvd, Downtown",
                "desc": "Overlooking Burj Khalifa and Dubai Fountain, 5-star luxury with cascading infinity pool and spa.",
                "price_multiplier": 1.03,
                "rating_offset": -0.1,
                "meals": "Room Only",
                "cancellation": "Non-Refundable",
                "room_type": "Deluxe Burj View"
            }
        ]
    },
    {
        "canonical_name": "Marina Byblos Hotel",
        "area": "Dubai Marina",
        "base_rating": 4.2,
        "base_price": 8500,
        "base_weekly_demand": 52,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Marina Byblos Hotel",
                "location": "Al Hubob St, Dubai Marina",
                "desc": "4-star marina hotel near JBR beach with rooftop swimming pool, traditional shisha lounge, and 6 restaurants.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Standard Double Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Marina Byblos Dubai",
                "location": "Dubai Marina Walk, Dubai",
                "desc": "Modern 4-star property minutes from Jumeirah Beach and DMCC metro station with city view rooms.",
                "price_multiplier": 0.96,
                "rating_offset": -0.1,
                "meals": "Room Only",
                "cancellation": "Non-Refundable",
                "room_type": "Executive Double"
            }
        ]
    },
    {
        "canonical_name": "Sofitel Dubai The Palm",
        "area": "Palm Jumeirah",
        "base_rating": 4.6,
        "base_price": 26000,
        "base_weekly_demand": 30,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Sofitel Dubai The Palm Resort",
                "location": "East Crescent, Palm Jumeirah, Dubai",
                "desc": "Polynesian-themed 5-star luxury resort with 500m private sandy beach, 6 outdoor pools, and Sofitel spa.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Half Board",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Luxury Palm View Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Sofitel Palm Dubai Luxury Resort",
                "location": "Palm Jumeirah, Dubai",
                "desc": "Beachfront French luxury resort surrounded by exotic lush gardens on Palm Jumeirah with luxury cabanas.",
                "price_multiplier": 1.05,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Junior Suite"
            },
            {
                "supplier": "OasisRooms B2B",
                "name": "Sofitel The Palm Resort & Spa",
                "location": "Palm Jumeirah East, Dubai",
                "desc": "Luxury beachfront resort with Polynesian architecture, Thalassotherapy spa pools, and watersports.",
                "price_multiplier": 0.97,
                "rating_offset": -0.1,
                "meals": "Room Only",
                "cancellation": "Non-Refundable",
                "room_type": "Classic Sea View"
            }
        ]
    },
    {
        "canonical_name": "Rove Downtown",
        "area": "Downtown Dubai",
        "base_rating": 4.5,
        "base_price": 7200,
        "base_weekly_demand": 60,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Rove Downtown Dubai",
                "location": "Al Sa'ada St, Downtown Dubai",
                "desc": "Trendy, lifestyle hotel next to Dubai Mall with 24-hr gym, Reel boutique cinema, and outdoor swimming pool.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Rover Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Rove Downtown Hotel",
                "location": "Downtown Dubai, Dubai",
                "desc": "Modern budget-friendly design hotel offering superfast WiFi, gym, laundromat, and Burj views.",
                "price_multiplier": 1.04,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Rover Room Burj View"
            }
        ]
    },
    {
        "canonical_name": "FIVE Palm Jumeirah",
        "area": "Palm Jumeirah",
        "base_rating": 4.5,
        "base_price": 31000,
        "base_weekly_demand": 40,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "FIVE Palm Jumeirah Dubai",
                "location": "No. 1 Palm Jumeirah, Dubai",
                "desc": "Glamorous lifestyle hotel with social pool, private beach, rooftop penthouse lounge, and high-energy nightlife.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Non-Refundable",
                "room_type": "Superior King Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "FIVE Palm Jumeirah",
                "location": "The Palm Jumeirah, Dubai",
                "desc": "Chic beachfront resort with dramatic glass cubes, private beach, fine dining, and party vibes.",
                "price_multiplier": 0.96,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Luxe Sea View Room"
            }
        ]
    },
    {
        "canonical_name": "Grosvenor House Dubai",
        "area": "Dubai Marina",
        "base_rating": 4.8,
        "base_price": 24000,
        "base_weekly_demand": 28,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Grosvenor House, a Luxury Collection Hotel",
                "location": "Al Emreef St, Dubai Marina, Dubai",
                "desc": "Sophisticated twin-tower hotel in Dubai Marina with B/Attitude spa, Michelin-starred Buddha Bar, and butler service.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Deluxe Room Tower 1"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Grosvenor House Hotel Dubai",
                "location": "Dubai Marina, Dubai",
                "desc": "Luxury marina accommodation with private beach access at sister property Le Royal Meridien.",
                "price_multiplier": 0.98,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Premier King Room"
            }
        ]
    },
    {
        "canonical_name": "Armani Hotel Dubai",
        "area": "Downtown Dubai",
        "base_rating": 4.7,
        "base_price": 55000,
        "base_weekly_demand": 18,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Armani Hotel Dubai",
                "location": "Burj Khalifa, Downtown Dubai",
                "desc": "Exclusive luxury hotel situated within Burj Khalifa designed personally by Giorgio Armani with private lifestyle managers.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Moderate (7 days)",
                "room_type": "Armani Classic Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Armani Hotel - Burj Khalifa",
                "location": "Downtown Dubai, Dubai",
                "desc": "Elegance and tailored service in the world's tallest tower with Armani spa and direct Dubai Mall access.",
                "price_multiplier": 1.05,
                "rating_offset": 0.0,
                "meals": "Half Board",
                "cancellation": "Non-Refundable",
                "room_type": "Armani Fountain Suite"
            }
        ]
    },
    {
        "canonical_name": "Grand Hyatt Dubai",
        "area": "Deira / Creek",
        "base_rating": 4.5,
        "base_price": 12500,
        "base_weekly_demand": 42,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Grand Hyatt Dubai",
                "location": "Riyadh Street, Dubai Creek, Dubai",
                "desc": "Resort-style city hotel set in 37 acres of landscaped gardens with 13 restaurants, indoor & outdoor swimming pools.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "1 King Bed Garden View"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Grand Hyatt Hotel Dubai",
                "location": "Bur Dubai / Creek, Dubai",
                "desc": "Family-friendly luxury hotel overlooking historic Dubai Creek with Ahasees luxury spa and club lounge.",
                "price_multiplier": 1.04,
                "rating_offset": -0.1,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Deluxe King Room"
            }
        ]
    },
    {
        "canonical_name": "Hilton Dubai Jumeirah",
        "area": "JBR (Jumeirah Beach Residence)",
        "base_rating": 4.4,
        "base_price": 19000,
        "base_weekly_demand": 36,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Hilton Dubai Jumeirah Resort",
                "location": "The Walk, JBR, Dubai",
                "desc": "Beachfront resort on The Walk with watersports, Wavebreaker beach bar, landscaped garden, and kids club.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "King Sea View Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Hilton Dubai JBR",
                "location": "Jumeirah Beach Residence, Dubai",
                "desc": "Beachfront stay on Dubai's famous promenade with private beach, shaded sunbeds, and ocean views.",
                "price_multiplier": 0.97,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Non-Refundable",
                "room_type": "Deluxe Walk View"
            }
        ]
    },
    {
        "canonical_name": "Novotel Dubai Al Barsha",
        "area": "Al Barsha",
        "base_rating": 4.2,
        "base_price": 6200,
        "base_weekly_demand": 55,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Novotel Dubai Al Barsha",
                "location": "Opposite Sharaf DG Metro, Al Barsha 1, Dubai",
                "desc": "4-star family hotel near Mall of the Emirates with heated outdoor pool, fitness centre, and 5 restaurants.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Superior Double Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Novotel Hotel Al Barsha Dubai",
                "location": "Sheikh Zayed Road, Al Barsha, Dubai",
                "desc": "Contemporary hotel near Mashreq metro and Ski Dubai with business centre and spa facilities.",
                "price_multiplier": 0.97,
                "rating_offset": -0.1,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Executive King"
            }
        ]
    },
    {
        "canonical_name": "Palace Downtown",
        "area": "Downtown Dubai",
        "base_rating": 4.8,
        "base_price": 38000,
        "base_weekly_demand": 24,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Palace Downtown",
                "location": "Sheikh Mohammed bin Rashid Blvd, Downtown Dubai",
                "desc": "Arabian-style palatial resort situated on Burj Lake with views of Dubai Fountain and Burj Khalifa.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Deluxe Lake View"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "The Palace Downtown Dubai",
                "location": "Downtown Dubai, Dubai",
                "desc": "Opulent Middle Eastern luxury facing Burj Khalifa with lakeside alfresco dining and oriental hammam.",
                "price_multiplier": 1.04,
                "rating_offset": -0.1,
                "meals": "Half Board",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Palace Lake Suite"
            }
        ]
    },
    {
        "canonical_name": "Premier Inn Dubai Al Jaddaf",
        "area": "Deira / Creek",
        "base_rating": 4.1,
        "base_price": 3800,
        "base_weekly_demand": 68,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Premier Inn Dubai Al Jaddaf",
                "location": "Culture Village, Al Jaddaf, Dubai",
                "desc": "Reliable modern budget hotel near Dubai Healthcare City with rooftop pool, Costa Coffee, and free mall shuttle.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Standard Double"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Premier Inn Al Jaddaf Hotel",
                "location": "Al Jaddaf, Dubai",
                "desc": "Value accommodation with comfortable Hypnos beds, all-day dining, and free shuttle to Dubai Mall and festival city.",
                "price_multiplier": 1.08,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Family Room"
            }
        ]
    },
    {
        "canonical_name": "Anantara The Palm Dubai Resort",
        "area": "Palm Jumeirah",
        "base_rating": 4.7,
        "base_price": 33000,
        "base_weekly_demand": 26,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Anantara The Palm Dubai Resort",
                "location": "East Crescent, Palm Jumeirah, Dubai",
                "desc": "Thai-inspired luxury resort featuring exclusive overwater villas, lagoon access rooms, and Asian culinary dining.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Premier Lagoon View"
            },
            {
                "supplier": "OasisRooms B2B",
                "name": "Anantara Palm Resort Dubai",
                "location": "Palm Jumeirah Crescent, Dubai",
                "desc": "Beach sanctuary with overwater villas, 3 temperature-controlled lagoon pools, and authentic Thai wellness spa.",
                "price_multiplier": 1.05,
                "rating_offset": -0.1,
                "meals": "Half Board",
                "cancellation": "Non-Refundable",
                "room_type": "Lagoon Access Room"
            }
        ]
    },
    {
        "canonical_name": "Ibis Mall of the Emirates",
        "area": "Al Barsha",
        "base_rating": 4.0,
        "base_price": 4200,
        "base_weekly_demand": 62,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Ibis Mall of the Emirates",
                "location": "Al Barsha 1, Near Mall of Emirates, Dubai",
                "desc": "Smart budget hotel directly adjacent to Mall of the Emirates and Ski Dubai with Italian restaurant and bar.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Standard Queen Room"
            },
            {
                "supplier": "OasisRooms B2B",
                "name": "Hotel Ibis Mall of Emirates",
                "location": "Barsha 1, Dubai",
                "desc": "Affordable city stay steps away from metro station and premier shopping, clean rooms with sweet bed concept.",
                "price_multiplier": 0.95,
                "rating_offset": -0.1,
                "meals": "Breakfast Included",
                "cancellation": "Non-Refundable",
                "room_type": "Standard Twin Room"
            }
        ]
    },
    {
        "canonical_name": "Shangri-La Dubai",
        "area": "Downtown Dubai",
        "base_rating": 4.6,
        "base_price": 21500,
        "base_weekly_demand": 32,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Shangri-La Dubai",
                "location": "Sheikh Zayed Road, Near Financial Centre, Dubai",
                "desc": "Asian-inspired luxury hospitality with panoramic Burj Khalifa views, Horizon Club lounge, and holistic spa.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Deluxe Sea View"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "Shangri-La Hotel Dubai",
                "location": "Sheikh Zayed Road, Downtown Dubai",
                "desc": "Luxury high-rise on Sheikh Zayed Road with luxury spa, squash courts, and premier Shang Palace Chinese dining.",
                "price_multiplier": 1.02,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Horizon Club Room"
            }
        ]
    },
    {
        "canonical_name": "Millennium Plaza Downtown Hotel",
        "area": "Business Bay",
        "base_rating": 4.3,
        "base_price": 9800,
        "base_weekly_demand": 46,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "Millennium Plaza Downtown Hotel",
                "location": "Sheikh Zayed Road, Trade Centre Area, Dubai",
                "desc": "Business and leisure tower hotel across from World Trade Centre with rooftop infinity pool and fitness club.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Superior King Room"
            },
            {
                "supplier": "OasisRooms B2B",
                "name": "Millennium Plaza Hotel Dubai",
                "location": "Sheikh Zayed Rd, Dubai",
                "desc": "Central Sheikh Zayed Rd location with spacious rooms, skyline vistas, and meeting facilities.",
                "price_multiplier": 0.96,
                "rating_offset": -0.1,
                "meals": "Room Only",
                "cancellation": "Non-Refundable",
                "room_type": "Deluxe Skyline View"
            }
        ]
    },
    {
        "canonical_name": "W Dubai - The Palm",
        "area": "Palm Jumeirah",
        "base_rating": 4.6,
        "base_price": 32000,
        "base_weekly_demand": 35,
        "variants": [
            {
                "supplier": "DirectBed Global",
                "name": "W Dubai - The Palm",
                "location": "West Crescent, Palm Jumeirah, Dubai",
                "desc": "Vibrant luxury beachfront escape featuring WET Deck pool parties, Michelin-starred dining, and AWAY Spa.",
                "price_multiplier": 1.0,
                "rating_offset": 0.0,
                "meals": "Room Only",
                "cancellation": "Free Cancellation (48 hrs)",
                "room_type": "Wonderful King Room"
            },
            {
                "supplier": "GulfTravel Wholesale",
                "name": "W The Palm Hotel Dubai",
                "location": "Palm Jumeirah West Crescent, Dubai",
                "desc": "Bold playful design with private beach, rooftop SoBe sunset lounge, and bespoke luxury suites.",
                "price_multiplier": 1.06,
                "rating_offset": 0.0,
                "meals": "Breakfast Included",
                "cancellation": "Free Cancellation (24 hrs)",
                "room_type": "Fabulous Sea View"
            }
        ]
    }
]

SUPPLIER_RELIABILITY = {
    "DirectBed Global": 0.95,
    "GulfTravel Wholesale": 0.88,
    "OasisRooms B2B": 0.82
}

def generate_raw_supplier_listings():
    """
    Generates synthetic dataset of 48 hotel listings across 3 fictional suppliers.
    Includes duplicates, realistic variation in titles, descriptions, pricing, meals, and policies.
    """
    records = []
    listing_id = 1001

    for h_idx, template in enumerate(HOTEL_TEMPLATES):
        canonical_id = f"HTL-{h_idx+1:03d}"
        for var in template["variants"]:
            supp = var["supplier"]
            price = int(round(template["base_price"] * var["price_multiplier"], -2))
            rating = round(min(5.0, max(3.0, template["base_rating"] + var["rating_offset"])), 1)
            
            records.append({
                "listing_id": f"LST-{listing_id}",
                "supplier": supp,
                "supplier_reliability": SUPPLIER_RELIABILITY[supp],
                "hotel_name": var["name"],
                "location": var["location"],
                "area": template["area"],
                "description": var["desc"],
                "price_inr": price,
                "rating": rating,
                "meals": var["meals"],
                "cancellation_policy": var["cancellation"],
                "room_type": var["room_type"],
                "_true_canonical_id": canonical_id,
                "_true_canonical_name": template["canonical_name"]
            })
            listing_id += 1

    df = pd.DataFrame(records)
    # Shuffle slightly to emulate real unsorted feed
    np.random.seed(42)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

def generate_historical_demand(master_hotels_df):
    """
    Generates 8 weeks of historical demand/bookings per canonical master hotel.
    Returns DataFrame: hotel_id, hotel_name, week_1 through week_8, avg_demand
    """
    np.random.seed(42)
    demand_records = []
    
    # Map canonical names to base demand
    base_demands = {t["canonical_name"]: t["base_weekly_demand"] for t in HOTEL_TEMPLATES}
    
    for _, row in master_hotels_df.iterrows():
        hid = row["master_hotel_id"]
        hname = row["canonical_name"]
        base = base_demands.get(hname, 35)
        
        # 8 weeks with realistic trend and random fluctuation
        weeks = []
        trend = np.linspace(-3, 4, 8) # slightly rising demand trend for Dubai high season
        for w in range(8):
            noise = np.random.randint(-5, 6)
            w_demand = max(5, int(round(base + trend[w] + noise)))
            weeks.append(w_demand)
            
        record = {
            "master_hotel_id": hid,
            "canonical_name": hname,
            "area": row["area"],
            "week_1": weeks[0],
            "week_2": weeks[1],
            "week_3": weeks[2],
            "week_4": weeks[3],
            "week_5": weeks[4],
            "week_6": weeks[5],
            "week_7": weeks[6],
            "week_8": weeks[7],
            "avg_weekly_demand": int(round(np.mean(weeks))),
            "last_week_demand": weeks[-1]
        }
        demand_records.append(record)
        
    return pd.DataFrame(demand_records)

if __name__ == "__main__":
    df = generate_raw_supplier_listings()
    print(f"Generated {len(df)} listings across {df['supplier'].nunique()} suppliers.")
    print(df[["listing_id", "supplier", "hotel_name", "price_inr", "rating"]].head())
