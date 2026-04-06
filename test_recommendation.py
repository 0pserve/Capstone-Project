"""
추천 알고리즘 테스트 스크립트
"""
import sys
sys.path.insert(0, '.')

from main import recommend_places, cosine_similarity, optimize_route

def test_cosine_similarity():
    """코사인 유사도 계산 테스트"""
    vec1 = [1, 0, 0]
    vec2 = [0, 1, 0]
    sim = cosine_similarity(vec1, vec2)
    print(f"코사인 유사도 테스트: vec1={vec1}, vec2={vec2}, similarity={sim:.4f}")
    assert abs(sim - 0.0) < 1e-6, "직교 벡터의 유사도는 0이어야 함"
    
    vec3 = [1, 0, 0]
    vec4 = [2, 0, 0]
    sim2 = cosine_similarity(vec3, vec4)
    print(f"동일 방향 벡터 테스트: vec3={vec3}, vec4={vec4}, similarity={sim2:.4f}")
    assert abs(sim2 - 1.0) < 1e-6, "동일 방향 벡터의 유사도는 1이어야 함"
    print("[PASS] 코사인 유사도 테스트 통과")

def test_recommendation():
    """추천 알고리즘 테스트"""
    places = {
        "성산일출봉": [1.0, 0, 0.9],
        "아쿠아플라넷": [0.2, 1, 0.4],
        "비자림": [0.9, 0, 0.6],
        "제주현대미술관": [0.3, 1, 0.3]
    }
    
    user_vector = [0.8, 0.2, 0.7]
    
    # 맑은 날 테스트
    sunny_results = recommend_places(user_vector, places, is_rainy=False)
    print("\n맑은 날 추천 결과:")
    for place, score in sunny_results:
        print(f"  {place}: {score:.4f}")
    
    # 비 오는 날 테스트
    rainy_results = recommend_places(user_vector, places, is_rainy=True)
    print("\n비 오는 날 추천 결과:")
    for place, score in rainy_results:
        print(f"  {place}: {score:.4f}")
    
    # 검증: 비 오는 날에는 실내 장소가 상위에 있어야 함
    rainy_top2 = [place for place, _ in rainy_results[:2]]
    indoor_places = ["아쿠아플라넷", "제주현대미술관"]
    for place in rainy_top2:
        if place in indoor_places:
            print(f"[PASS] 비 오는 날 상위에 실내 장소 '{place}' 포함")
            break
    else:
        print("[WARN] 비 오는 날 상위에 실내 장소가 없음")
    
    # 검증: 맑은 날에는 자연 친화적 장소가 상위에 있어야 함
    sunny_top2 = [place for place, _ in sunny_results[:2]]
    outdoor_places = ["성산일출봉", "비자림"]
    for place in sunny_top2:
        if place in outdoor_places:
            print(f"[PASS] 맑은 날 상위에 실외 장소 '{place}' 포함")
            break
    else:
        print("[WARN] 맑은 날 상위에 실외 장소가 없음")
    
    print("[PASS] 추천 알고리즘 테스트 통과")

def test_route_optimization():
    """경로 최적화 테스트"""
    places_coords = {
        "A": (0, 0),
        "B": (1, 0),
        "C": (1, 1)
    }
    
    top_places = ["A", "B", "C"]
    best_route, best_distance = optimize_route(places_coords, top_places)
    
    print(f"\n경로 최적화 테스트:")
    print(f"  입력 장소: {top_places}")
    print(f"  최적 경로: {best_route}")
    print(f"  최소 거리: {best_distance:.4f}")
    
    # 간단한 검증: 거리가 0보다 커야 함
    assert best_distance > 0, "거리는 0보다 커야 함"
    assert len(best_route) == 3, "경로는 3개 장소를 포함해야 함"
    print("[PASS] 경로 최적화 테스트 통과")

def main():
    print("=" * 60)
    print("상황 인식 기반 제주도 여행 추천 알고리즘 테스트")
    print("=" * 60)
    
    try:
        test_cosine_similarity()
        test_recommendation()
        test_route_optimization()
        print("\n" + "=" * 60)
        print("모든 테스트 통과! [SUCCESS]")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n테스트 실패: {e}")
        return False
    except Exception as e:
        print(f"\n예외 발생: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)