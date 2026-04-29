"""
Real-world data validation test for Jeju recommendation system.
Uses the tagged CSV dataset (jeju_all_tagged_places.csv) to verify algorithm performance.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import random
import math
from typing import List, Tuple, Dict
from app.repositories import InMemoryPlaceRepository
from app.services import recommend_places, optimize_route, calculate_distance


def load_real_data():
    """Load repository with CSV data."""
    repo = InMemoryPlaceRepository()
    places = repo.get_all_places()
    places_coords = repo.get_place_coordinates()
    return repo, places, places_coords


def case1_rainy_day_indoor_ratio():
    """
    CASE 1 (Rainy day ranking change):
    When weather is 'rain', compute the ratio of 'indoor' tagged places
    among top-10 recommendations, compared to clear weather.
    """
    repo, places, _ = load_real_data()
    
    # User vector: neutral preference
    user = [0.5, 0.5, 0.5]
    
    # Clear weather (is_rainy=False)
    clear_rec = recommend_places(user, places, is_rainy=False)
    clear_top10 = [place for place, _ in clear_rec[:10]]
    
    # Rainy weather (is_rainy=True)
    rainy_rec = recommend_places(user, places, is_rainy=True)
    rainy_top10 = [place for place, _ in rainy_rec[:10]]
    
    # Count indoor places (tag == 'indoor')
    # We need to know tag of each place; we can infer from vector[1] (indoor flag)
    def indoor_count(place_names):
        count = 0
        for name in place_names:
            place = places.get(name)
            if place and place.vector[1] > 0.5:  # indoor flag > 0.5
                count += 1
        return count
    
    clear_indoor = indoor_count(clear_top10)
    rainy_indoor = indoor_count(rainy_top10)
    
    clear_ratio = clear_indoor / 10.0
    rainy_ratio = rainy_indoor / 10.0
    
    increase_factor = rainy_ratio / clear_ratio if clear_ratio > 0 else float('inf')
    
    print("\n=== CASE 1: Rainy Day Indoor Ratio ===")
    print(f"Clear weather top-10 indoor count: {clear_indoor} ({clear_ratio:.1%})")
    print(f"Rainy weather top-10 indoor count: {rainy_indoor} ({rainy_ratio:.1%})")
    print(f"Increase factor: {increase_factor:.2f}x")
    
    return {
        "clear_indoor": clear_indoor,
        "rainy_indoor": rainy_indoor,
        "increase_factor": increase_factor
    }


def case2_nature_preference_hit():
    """
    CASE 2 (Preference accuracy):
    For a user with high nature score, verify that places like '비자림', '사려니숲길'
    appear within top-5 recommendations.
    """
    repo, places, _ = load_real_data()
    
    # High nature preference vector [nature, indoor, activity]
    nature_lover = [0.9, 0.1, 0.3]
    
    rec = recommend_places(nature_lover, places, is_rainy=False)
    top5 = [place for place, _ in rec[:5]]
    
    target_places = ["비자림", "사려니숲길"]
    found = [p for p in target_places if p in top5]
    
    print("\n=== CASE 2: Nature Preference Hit ===")
    print(f"Nature-lover top-5: {top5}")
    print(f"Target places: {target_places}")
    print(f"Found in top-5: {found}")
    print(f"Hit rate: {len(found)}/{len(target_places)}")
    
    return {
        "top5": top5,
        "target_places": target_places,
        "found": found,
        "hit_rate": len(found) / len(target_places)
    }


def case3_route_optimization_efficiency():
    """
    CASE 3 (Route optimization efficiency):
    Randomly pick 5 places from eastern/western Jeju, compute travel distance
    with and without TSP optimization, report reduction in km.
    """
    repo, places, places_coords = load_real_data()
    
    # Filter places by approximate region (east: longitude > 126.8, west: < 126.4)
    east_places = []
    west_places = []
    for name, coords in places_coords.items():
        lon = coords[1]  # longitude
        if lon > 126.8:
            east_places.append(name)
        elif lon < 126.4:
            west_places.append(name)
    
    # Randomly select 5 places (mix east/west)
    selected = []
    if len(east_places) >= 3:
        selected.extend(random.sample(east_places, 3))
    if len(west_places) >= 2:
        selected.extend(random.sample(west_places, 2))
    if len(selected) < 5:
        # fallback: any 5 places
        all_names = list(places_coords.keys())
        selected = random.sample(all_names, 5)
    
    # Distance without optimization (original order)
    dist_original = 0.0
    for i in range(len(selected) - 1):
        c1 = places_coords[selected[i]]
        c2 = places_coords[selected[i + 1]]
        dist_original += calculate_distance(c1, c2)
    
    # Optimized route
    optimized_order, dist_optimized = optimize_route(places_coords, selected)
    
    reduction = dist_original - dist_optimized
    reduction_percent = (reduction / dist_original * 100) if dist_original > 0 else 0.0
    
    print("\n=== CASE 3: Route Optimization Efficiency ===")
    print(f"Selected places (original order): {selected}")
    print(f"Optimized order: {optimized_order}")
    print(f"Original distance: {dist_original:.2f} km")
    print(f"Optimized distance: {dist_optimized:.2f} km")
    print(f"Distance reduction: {reduction:.2f} km ({reduction_percent:.1f}%)")
    
    return {
        "original_distance_km": dist_original,
        "optimized_distance_km": dist_optimized,
        "reduction_km": reduction,
        "reduction_percent": reduction_percent
    }


def generate_report(results1, results2, results3):
    """Generate a summary report suitable for professor presentation."""
    print("\n" + "="*60)
    print("REAL-DATA VALIDATION REPORT")
    print("="*60)
    
    # Extract metrics
    indoor_increase = results1.get("increase_factor", 0)
    hit_rate = results2.get("hit_rate", 0)
    avg_reduction = results3.get("reduction_km", 0)
    
    # Format summary
    summary = (
        f"Real-data validation results: "
        f"Average travel distance reduced by {avg_reduction:.1f} km, "
        f"Indoor place exposure frequency increased {indoor_increase:.1f}x on rainy days, "
        f"Nature-preference hit rate {hit_rate:.1%}."
    )
    
    print(summary)
    print("\nDetailed metrics:")
    print(f"  - Rainy day indoor ratio increase: {indoor_increase:.2f}x")
    print(f"  - Nature-preference hit rate: {hit_rate:.1%}")
    print(f"  - Route optimization distance reduction: {avg_reduction:.2f} km")
    print("="*60)
    
    return summary


def main():
    """Run all three cases and produce report."""
    print("Starting real-data validation tests...")
    
    # Run cases
    r1 = case1_rainy_day_indoor_ratio()
    r2 = case2_nature_preference_hit()
    r3 = case3_route_optimization_efficiency()
    
    # Generate report
    report = generate_report(r1, r2, r3)
    
    # Return combined results for possible external use
    return {
        "case1": r1,
        "case2": r2,
        "case3": r3,
        "report": report
    }


if __name__ == "__main__":
    main()