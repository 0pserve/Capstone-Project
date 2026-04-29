"""
상황 인식 기반 제주도 여행 추천 알고리즘 프로토타입
Capstone Design Project: 상황 대응형 제주 여행 플래너
"""

import numpy as np
from scipy.spatial.distance import cosine
from itertools import permutations
import math

def cosine_similarity(vec1, vec2):
    """코사인 유사도 계산 (Scipy의 cosine 거리 사용)"""
    # scipy.spatial.distance.cosine은 코사인 거리(1 - 유사도)를 반환
    # 유사도 = 1 - 코사인 거리
    cos_dist = cosine(vec1, vec2)
    return 1 - cos_dist

def calculate_distance(coord1, coord2):
    """두 좌표 간의 유클리드 거리 계산 (단순화)"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

def recommend_places(user_vector, places_dict, is_rainy=False):
    """
    사용자 취향과 상황(비 여부)을 고려한 장소 추천
    
    Args:
        user_vector: 사용자 취향 벡터 [자연 선호, 실내 선호, 활동성 선호]
        places_dict: 장소 이름을 키로, [자연친화도, 실내여부, 활동성] 벡터를 값으로 하는 딕셔너리
        is_rainy: 비 오는 날 여부
    
    Returns:
        정렬된 (장소 이름, 최종 점수) 리스트
    """
    results = []
    
    for place_name, place_vector in places_dict.items():
        # 기본 코사인 유사도 계산
        base_score = cosine_similarity(user_vector, place_vector)
        
        # 상황 가중치 적용
        final_score = base_score
        
        if is_rainy:
            indoor_flag = place_vector[1]  # 실내여부 (0 or 1)
            if indoor_flag == 0:  # 실외 장소
                final_score *= 0.3  # 70% 감점 (30%만 남음)
            else:  # 실내 장소
                final_score *= 1.5  # 50% 가중치 (150%)
        
        results.append((place_name, final_score))
    
    # 내림차순 정렬 (높은 점수 순)
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def optimize_route(places_coords, top_places):
    """
    상위 3개 장소의 방문 순서를 최적화 (단순 TSP)
    
    Args:
        places_coords: 장소 이름을 키로, (위도, 경도) 튜플을 값으로 하는 딕셔너리
        top_places: 상위 3개 장소 이름 리스트
    
    Returns:
        최적 순서와 총 거리
    """
    if len(top_places) < 2:
        return top_places, 0
    
    # 모든 가능한 순열 생성
    best_route = None
    best_distance = float('inf')
    
    for perm in permutations(top_places):
        total_distance = 0
        for i in range(len(perm) - 1):
            coord1 = places_coords[perm[i]]
            coord2 = places_coords[perm[i + 1]]
            total_distance += calculate_distance(coord1, coord2)
        
        if total_distance < best_distance:
            best_distance = total_distance
            best_route = perm
    
    return list(best_route), best_distance

def main():
    print("=" * 60)
    print("상황 인식 기반 제주도 여행 추천 알고리즘 프로토타입")
    print("=" * 60)
    
    # 1. 데이터 정의 (Vectorization)
    places = {
        "성산일출봉": [1.0, 0, 0.9],    # 자연친화도 1.0, 실내여부 0, 활동성 0.9
        "아쿠아플라넷": [0.2, 1, 0.4],  # 자연친화도 0.2, 실내여부 1, 활동성 0.4
        "비자림": [0.9, 0, 0.6],       # 자연친화도 0.9, 실내여부 0, 활동성 0.6
        "제주현대미술관": [0.3, 1, 0.3] # 자연친화도 0.3, 실내여부 1, 활동성 0.3
    }
    
    # 2. 사용자 프로필
    user_vector = [0.8, 0.2, 0.7]  # [자연 선호, 실내 선호, 활동성 선호]
    
    # 3. 장소 좌표 (임의 설정)
    places_coords = {
        "성산일출봉": (33.458, 126.942),
        "아쿠아플라넷": (33.240, 126.427),
        "비자림": (33.487, 126.809),
        "제주현대미술관": (33.511, 126.523)
    }
    
    print("\n[데이터 정의]")
    print(f"사용자 취향 벡터: {user_vector}")
    print("\n장소 벡터:")
    for place, vector in places.items():
        print(f"  {place}: {vector}")
    
    # 4. 맑은 날 추천
    print("\n" + "=" * 60)
    print("맑은 날 (is_rainy=False) 추천 결과")
    print("=" * 60)
    
    sunny_recommendations = recommend_places(user_vector, places, is_rainy=False)
    
    for i, (place, score) in enumerate(sunny_recommendations, 1):
        print(f"{i}. {place}: {score:.4f}")
    
    top3_sunny = [place for place, _ in sunny_recommendations[:3]]
    print(f"\n상위 3개 장소: {top3_sunny}")
    
    # 5. 비 오는 날 추천
    print("\n" + "=" * 60)
    print("비 오는 날 (is_rainy=True) 추천 결과")
    print("=" * 60)
    
    rainy_recommendations = recommend_places(user_vector, places, is_rainy=True)
    
    for i, (place, score) in enumerate(rainy_recommendations, 1):
        print(f"{i}. {place}: {score:.4f}")
    
    top3_rainy = [place for place, _ in rainy_recommendations[:3]]
    print(f"\n상위 3개 장소: {top3_rainy}")
    
    # 6. 경로 최적화 시뮬레이션
    print("\n" + "=" * 60)
    print("경로 최적화 시뮬레이션 (단순 TSP)")
    print("=" * 60)
    
    # 맑은 날 상위 3개 장소 경로 최적화
    sunny_route, sunny_distance = optimize_route(places_coords, top3_sunny)
    print(f"\n맑은 날 최적 방문 경로:")
    print(f"  순서: {' → '.join(sunny_route)}")
    print(f"  총 거리: {sunny_distance:.4f}")
    
    # 비 오는 날 상위 3개 장소 경로 최적화
    rainy_route, rainy_distance = optimize_route(places_coords, top3_rainy)
    print(f"\n비 오는 날 최적 방문 경로:")
    print(f"  순서: {' → '.join(rainy_route)}")
    print(f"  총 거리: {rainy_distance:.4f}")
    
    # 7. 비교 분석
    print("\n" + "=" * 60)
    print("비교 분석")
    print("=" * 60)
    
    print("\n맑은 날 vs 비 오는 날 순위 변화:")
    print(f"{'장소':<15} {'맑은날 순위':<12} {'비오는날 순위':<12} {'변화':<10}")
    print("-" * 50)
    
    sunny_rank = {place: i+1 for i, (place, _) in enumerate(sunny_recommendations)}
    rainy_rank = {place: i+1 for i, (place, _) in enumerate(rainy_recommendations)}
    
    for place in places.keys():
        sunny_r = sunny_rank[place]
        rainy_r = rainy_rank[place]
        change = rainy_r - sunny_r
        change_str = f"▲{abs(change)}" if change < 0 else f"▼{abs(change)}" if change > 0 else "변화없음"
        print(f"{place:<15} {sunny_r:<12} {rainy_r:<12} {change_str:<10}")
    
    print("\n" + "=" * 60)
    print("알고리즘 설명:")
    print("=" * 60)
    print("""
1. 기본 추천: 사용자 취향 벡터와 장소 벡터 간의 코사인 유사도 계산
2. 상황 가중치: 비 오는 날(is_rainy=True)인 경우
   - 실외 장소(실내여부=0): 점수 70% 감점 (원래 점수의 30%)
   - 실내 장소(실내여부=1): 점수 50% 가중치 (원래 점수의 150%)
3. 경로 최적화: 상위 3개 장소에 대해 모든 가능한 순열을 검토하여
   총 이동 거리가 최소가 되는 순서 찾기 (단순 TSP)
    """)
    
    return sunny_recommendations, rainy_recommendations

if __name__ == "__main__":
    sunny_rec, rainy_rec = main()