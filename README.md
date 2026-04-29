# 상황 인식 기반 제주도 여행 추천 알고리즘

> Capstone Design Project: 상황 대응형 제주 여행 플래너

FastAPI 기반의 RESTful API 서버로, 사용자의 취향 벡터와 날씨 상황에 맞는 제주도 여행 장소를 추천하고 최적 방문 경로를 제공합니다.

## 📋 목차

- [기능](#-기능)
- [프로젝트 구조](#-프로젝트-구조)
- [설치](#-설치)
- [서버 실행](#-서버-실행)
- [API 사용법](#-api-사용법)
- [알고리즘 설명](#-알고리즘-설명)
- [확장 가이드](#-확장-가이드)
- [기술 스택](#-기술-스택)

## 🎯 기능

- **취향 기반 장소 추천**: 사용자의 취향 벡터(자연 선호, 실내 선호, 활동성 선호)와 장소 벡터 간 코사인 유사도 계산
- **상황 인식 가중치**: 비 오는 날 실내 장소 가중치 부여, 실외 장소 감점
- **경로 최적화 (TSP)**: 추천 장소 간 최소 이동 거리 방문 순서 계산
- **실시간 날씨 연동**: OpenWeatherMap API를 통한 날씨 정보 조회 (스켈레톤 구현)

## 📁 프로젝트 구조

```
capstone/
├── app/
│   ├── __init__.py              # 앱 패키지 초기화
│   ├── main.py                  # FastAPI 애플리케이션 및 엔드포인트
│   ├── models.py                # Pydantic Request/Response 모델 정의
│   ├── repositories.py          # Repository 패턴 (장소 데이터 접근 계층)
│   └── services.py              # 서비스 로직 (추천 알고리즘 + 날씨 API)
├── main.py                      # 기존 프로토타입 코드 (보존)
├── main_backup.py               # 원본 프로토타입 백업
├── requirements.txt             # Python 의존성
├── test_recommendation.py       # 알고리즘 테스트
└── README.md                    # 프로젝트 문서
```

## 🚀 설치

### 필수 요구사항

- Python 3.11+
- pip

### 의존성 설치

```bash
pip install -r requirements.txt
```

## 🖥️ 서버 실행

### 개발 서버 (자동 리로드)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 프로덕션 서버

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

서버 실행 후 다음 URL에서 API 문서 확인:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📡 API 사용법

### 1. 여행 장소 추천

**Endpoint**: `POST /recommend`

**Request Body**:

| 필드 | 타입 | 필수 | 설명 | 기본값 |
|------|------|------|------|--------|
| `user_vector` | `float[3]` | ✅ | 사용자 취향 벡터 `[자연 선호, 실내 선호, 활동성 선호]` | - |
| `is_rainy` | `bool` | ❌ | 비 오는 날 여부 | `false` |
| `top_n` | `int` | ❌ | 추천할 장소 수 (1~10) | `3` |

**Request 예시**:

```json
{
  "user_vector": [0.8, 0.2, 0.7],
  "is_rainy": false,
  "top_n": 3
}
```

**Response 예시**:

```json
{
  "recommended_places": [
    {
      "name": "성산일출봉",
      "vector": [1.0, 0.0, 0.9],
      "coordinates": [33.458, 126.942],
      "score": 0.9827
    },
    {
      "name": "비자림",
      "vector": [0.9, 0.0, 0.6],
      "coordinates": [33.487, 126.809],
      "score": 0.9744
    },
    {
      "name": "제주현대미술관",
      "vector": [0.3, 1.0, 0.3],
      "coordinates": [33.511, 126.523],
      "score": 0.5532
    }
  ],
  "optimized_route": ["성산일출봉", "비자림", "제주현대미술관"],
  "total_distance": 0.4231,
  "is_rainy": false,
  "message": "맑은 날 야외 추천입니다."
}
```

**cURL 예시**:

```bash
# 맑은 날 추천
curl -X POST "http://127.0.0.1:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"user_vector": [0.8, 0.2, 0.7], "is_rainy": false, "top_n": 3}'

# 비 오는 날 추천
curl -X POST "http://127.0.0.1:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"user_vector": [0.8, 0.2, 0.7], "is_rainy": true, "top_n": 3}'
```

### 2. 날씨 정보 조회

**Endpoint**: `GET /weather`

**Query Parameters**:

| 필드 | 타입 | 필수 | 설명 | 기본값 |
|------|------|------|------|--------|
| `api_key` | `string` | ✅ | OpenWeatherMap API 키 | - |
| `lat` | `float` | ❌ | 위도 | `33.3642` (제주도 중심) |
| `lon` | `float` | ❌ | 경도 | `126.5553` (제주도 중심) |

**cURL 예시**:

```bash
curl "http://127.0.0.1:8000/weather?api_key=YOUR_API_KEY"
```

### 3. 장소 목록 조회

**Endpoint**: `GET /places`

**cURL 예시**:

```bash
curl "http://127.0.0.1:8000/places"
```

## 🧠 알고리즘 설명

### 1. 코사인 유사도 기반 추천

사용자 취향 벡터 `U = [자연 선호, 실내 선호, 활동성 선호]`와 장소 벡터 `P = [자연친화도, 실내여부, 활동성]` 간 코사인 유사도를 계산합니다.

```
cosine_similarity(U, P) = 1 - cosine_distance(U, P)
```

### 2. 상황 가중치 적용

비 오는 날 (`is_rainy=True`)에는 다음 가중치를 적용합니다:

| 장소 유형 | 조건 | 가중치 |
|-----------|------|--------|
| 실외 장소 | `indoor_flag = 0` | `score × 0.3` (70% 감점) |
| 실내 장소 | `indoor_flag = 1` | `score × 1.5` (50% 가중치) |

### 3. TSP 기반 경로 최적화

추천된 상위 N개 장소에 대해 모든 가능한 순열(permutation)을 검토하여 총 이동 거리가 최소가 되는 방문 순서를 찾습니다.

```
distance = Σ calculate_distance(coord[i], coord[i+1])
```

## 🔧 확장 가이드

### SQLite DB 연결

[`app/repositories.py`](app/repositories.py)에 [`SQLitePlaceRepository`](app/repositories.py:97) 클래스가 스켈레톤으로 준비되어 있습니다.

```python
from app.repositories import SQLitePlaceRepository

# DB 파일 경로 지정
repo = SQLitePlaceRepository(db_path="places.db")
```

### CSV 파일 연결

[`CSVPlaceRepository`](app/repositories.py:123)를 사용하여 CSV 파일에서 장소 데이터를 로드할 수 있습니다.

```python
from app.repositories import CSVPlaceRepository

repo = CSVPlaceRepository(csv_path="places.csv")
```

### OpenWeatherMap API 연동

[`app/services.py`](app/services.py)의 [`get_weather()`](app/services.py:97) 함수에서 주석을 해제하고 API 키를 설정하면 실제 날씨 데이터를 조회할 수 있습니다.

```python
# app/services.py에서 httpx 주석 해제
import httpx

# 실제 API 호출 코드 활성화
```

### 장소 데이터 추가

```python
from app.repositories import InMemoryPlaceRepository

repo = InMemoryPlaceRepository()
repo.add_place(
    name="새로운 장소",
    vector=[0.5, 0.0, 0.8],  # [자연친화도, 실내여부, 활동성]
    coordinates=(33.500, 126.600)  # (위도, 경도)
)
```

## 🛠️ 기술 스택

| 분야 | 기술 |
|------|------|
| 웹 프레임워크 | FastAPI |
| 데이터 과학 | NumPy, SciPy |
| 데이터 검증 | Pydantic |
| HTTP 클라이언트 | httpx, requests |
| 서버 | Uvicorn (ASGI) |

## 📄 라이선스

Capstone Design Project - 상황 대응형 제주 여행 플래너
