#!/usr/bin/env python3
"""
Debug script to analyze why '비자림', '사려니숲길' are not recommended.
Extracts vector values for key landmarks and lists top 20 nature-score places.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import csv
from collections import defaultdict

CSV_PATH = "jeju_all_tagged_places.csv"

def tag_to_vector(tag: str):
    """Same mapping as in app/repositories.py"""
    if tag == "indoor":
        return [0.2, 1.0, 0.3]   # [nature, indoor, activity]
    else:  # outdoor
        return [0.8, 0.0, 0.7]

def load_places():
    """Load all places with vectors from CSV."""
    places = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['title']
            tag = row['tag']
            vector = tag_to_vector(tag)
            places.append((title, vector, tag))
    return places

def main():
    print("=== DEBUG: Key Landmark Vectors ===")
    landmarks = ["비자림", "사려니숲길", "절물자연휴양림"]
    places = load_places()
    
    found = []
    for title, vector, tag in places:
        if title in landmarks:
            print(f"{title}: vector {vector} (tag: {tag})")
            found.append(title)
    
    for lm in landmarks:
        if lm not in found:
            print(f"{lm}: NOT FOUND in CSV")
    
    print("\n=== Top 20 Nature Score Places ===")
    # Sort by nature score (vector[0]) descending
    sorted_places = sorted(places, key=lambda x: x[1][0], reverse=True)
    for i, (title, vector, tag) in enumerate(sorted_places[:20]):
        print(f"{i+1:2d}. {title[:40]:40} nature={vector[0]:.2f} indoor={vector[1]:.2f} activity={vector[2]:.2f} tag={tag}")
    
    # Check where '비자림' ranks
    for i, (title, vector, tag) in enumerate(sorted_places):
        if title == "비자림":
            print(f"\n'비자림' rank: {i+1} (nature score {vector[0]})")
            break
    
    # Also show top 5 places that outrank 비자림
    print("\nTop 5 places outranking 비자림:")
    for i, (title, vector, tag) in enumerate(sorted_places[:5]):
        print(f"  {title} (nature={vector[0]:.2f})")
    
    # Count indoor/outdoor in top 20
    outdoor_count = sum(1 for _, _, tag in sorted_places[:20] if tag == "outdoor")
    indoor_count = 20 - outdoor_count
    print(f"\nTop 20 composition: outdoor={outdoor_count}, indoor={indoor_count}")
    
    # Additional: check if '사려니숲길' exists
    for title, vector, tag in places:
        if "사려니" in title:
            print(f"\nFound similar to 사려니숲길: {title} (tag {tag})")
    
    return places

if __name__ == "__main__":
    main()