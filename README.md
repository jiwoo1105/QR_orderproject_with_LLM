# 학식당 챗봇 API

대학교 학생식당 관리 시스템을 위한 AI 챗봇 API 서버입니다. ChatGPT API를 활용하여 메뉴 안내, 영양 정보 제공, 메뉴 추천 등의 기능을 제공합니다.

## 주요 기능

- 자연어 기반 학식당 정보 안내
- 메뉴, 가격, 영양 정보 제공
- 사용자 선호도 기반 메뉴 추천
- 대화 히스토리 관리
- RESTful API 제공

## 기술 스택

- Python 3.11+
- FastAPI
- OpenAI GPT-4
- Pydantic
- Uvicorn

## 프로젝트 구조

```
LLM_Project/
├── main.py                 # FastAPI 앱 및 엔드포인트
├── chatbot_service.py      # 챗봇 비즈니스 로직
├── models.py               # Pydantic 데이터 모델
├── config.py               # 설정 관리
├── requirements.txt        # 의존성 패키지
├── .env.example           # 환경변수 예시
├── Dockerfile             # Docker 이미지 빌드
├── docker-compose.yml     # Docker Compose 설정
└── README.md              # 프로젝트 문서
```

## 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론 (또는 프로젝트 디렉토리로 이동)
cd /Users/ziuuu/Documents/LLM_Project

# .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 OpenAI API 키 설정
# OPENAI_API_KEY=your_actual_api_key_here
```

### 2. 가상환경 생성 및 의존성 설치

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 서버 실행

#### 방법 1: Python으로 직접 실행

```bash
python main.py
```

#### 방법 2: Uvicorn으로 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 방법 3: 실행 스크립트 사용

```bash
chmod +x run.sh
./run.sh
```

#### 방법 4: Docker로 실행

```bash
# Docker 이미지 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 4. API 문서 확인

서버 실행 후 브라우저에서 접속:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 1. 헬스체크

```http
GET /health
```

서버 상태 확인

**응답 예시:**
```json
{
  "status": "healthy",
  "message": "API 서버 정상 작동 중 (API Key: configured)"
}
```

### 2. 챗봇 대화

```http
POST /chat
Content-Type: application/json
```

**요청 바디:**
```json
{
  "message": "오늘 메뉴가 뭐예요?",
  "conversation_history": [
    {
      "role": "user",
      "content": "안녕하세요"
    },
    {
      "role": "assistant",
      "content": "안녕하세요! 학생식당 안내 챗봇입니다."
    }
  ],
  "context": {
    "menus": [
      {
        "name": "김치찌개",
        "price": 5000,
        "calories": 450
      },
      {
        "name": "제육볶음",
        "price": 5500,
        "calories": 520
      }
    ],
    "operating_hours": {
      "조식": "08:00 - 09:30",
      "중식": "11:30 - 13:30",
      "석식": "17:30 - 19:00"
    },
    "location": "학생회관 1층"
  }
}
```

**응답 예시:**
```json
{
  "response": "오늘 메뉴는 김치찌개(5,000원)와 제육볶음(5,500원)이 준비되어 있습니다. 김치찌개는 450kcal, 제육볶음은 520kcal입니다.",
  "model": "gpt-4-turbo-preview",
  "tokens_used": 245,
  "error": null
}
```

### 3. 메뉴 추천

```http
POST /recommend
Content-Type: application/json
```

**요청 바디:**
```json
{
  "dietary_restrictions": ["견과류 알레르기"],
  "preferred_cuisine": "한식",
  "budget": 6000,
  "available_menus": [
    {
      "name": "김치찌개",
      "price": 5000,
      "calories": 450
    },
    {
      "name": "제육볶음",
      "price": 5500,
      "calories": 520
    }
  ]
}
```

**응답 예시:**
```json
{
  "response": "예산과 선호도를 고려하여 김치찌개를 추천드립니다. 한식 메뉴이며 가격도 5,000원으로 예산 내에 있고, 견과류가 포함되지 않아 안심하고 드실 수 있습니다.",
  "model": "gpt-4-turbo-preview",
  "tokens_used": 198,
  "error": null
}
```

### 4. 간단한 대화 (테스트용)

```http
POST /chat/simple?message=안녕하세요
```

**응답 예시:**
```json
{
  "response": "안녕하세요! 학생식당 안내 챗봇입니다. 무엇을 도와드릴까요?",
  "model": "gpt-4-turbo-preview",
  "tokens_used": 87
}
```

## Spring Boot에서 호출하기

### RestTemplate 사용 예시

```java
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;
import java.util.*;

@Service
public class ChatbotService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String CHATBOT_API_URL = "http://localhost:8000";

    public ChatResponse chat(String userMessage, List<Map<String, String>> history, Map<String, Object> context) {
        String url = CHATBOT_API_URL + "/chat";

        Map<String, Object> request = new HashMap<>();
        request.put("message", userMessage);
        request.put("conversation_history", history);
        request.put("context", context);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

        ResponseEntity<ChatResponse> response = restTemplate.postForEntity(
            url,
            entity,
            ChatResponse.class
        );

        return response.getBody();
    }
}
```

### WebClient 사용 예시 (Spring WebFlux)

```java
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class ChatbotService {

    private final WebClient webClient;

    public ChatbotService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
            .baseUrl("http://localhost:8000")
            .build();
    }

    public Mono<ChatResponse> chat(ChatRequest request) {
        return webClient.post()
            .uri("/chat")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .retrieve()
            .bodyToMono(ChatResponse.class);
    }
}
```

### DTO 클래스

```java
// ChatRequest.java
public class ChatRequest {
    private String message;
    private List<Message> conversationHistory;
    private Map<String, Object> context;

    // getters, setters, constructors
}

// Message.java
public class Message {
    private String role;
    private String content;

    // getters, setters, constructors
}

// ChatResponse.java
public class ChatResponse {
    private String response;
    private String model;
    private int tokensUsed;
    private String error;

    // getters, setters, constructors
}
```

## 환경변수 설정

`.env` 파일에서 설정 가능한 환경변수:

```env
# OpenAI API 설정
OPENAI_API_KEY=sk-...           # OpenAI API 키 (필수)
MODEL_NAME=gpt-4-turbo-preview  # 사용할 모델 (기본값)
MAX_TOKENS=1000                 # 최대 토큰 수
TEMPERATURE=0.7                 # 응답 창의성 (0.0-1.0)

# 서버 설정
HOST=0.0.0.0                    # 서버 호스트
PORT=8000                       # 서버 포트
```

## 커스터마이징

### 시스템 프롬프트 수정

`chatbot_service.py` 파일의 `system_prompt` 변수를 수정하여 챗봇의 페르소나와 응답 스타일을 변경할 수 있습니다.

```python
self.system_prompt = """
당신은 대학교 학생식당 관리 시스템의 친절한 AI 어시스턴트입니다.
# 여기에 원하는 지시사항 추가
"""
```

### 컨텍스트 포맷 변경

`_format_context` 메서드를 수정하여 백엔드에서 전달받는 데이터 구조에 맞게 조정할 수 있습니다.

## 테스트

### cURL로 테스트

```bash
# 헬스체크
curl http://localhost:8000/health

# 간단한 대화
curl -X POST "http://localhost:8000/chat/simple?message=안녕하세요"

# 전체 기능 테스트
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "오늘 메뉴 추천해주세요",
    "context": {
      "menus": [
        {"name": "김치찌개", "price": 5000, "calories": 450}
      ]
    }
  }'
```

### Python으로 테스트

```python
import requests

url = "http://localhost:8000/chat"
payload = {
    "message": "오늘 메뉴가 뭐예요?",
    "context": {
        "menus": [
            {"name": "김치찌개", "price": 5000}
        ]
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

## 트러블슈팅

### API 키 오류
- `.env` 파일에 올바른 OpenAI API 키가 설정되어 있는지 확인
- API 키에 충분한 크레딧이 있는지 확인

### 포트 충돌
- 8000번 포트가 이미 사용 중인 경우 `.env` 파일에서 `PORT` 변경

### CORS 오류
- `main.py`의 `allow_origins`에 백엔드 서버의 도메인 추가

## 배포

### 프로덕션 설정

프로덕션 환경에서는 다음 사항을 고려하세요:

1. CORS 설정을 구체적인 도메인으로 제한
2. 환경변수를 안전하게 관리 (Secrets Manager 사용)
3. 로깅 및 모니터링 추가
4. Rate limiting 구현
5. HTTPS 사용

## 라이선스

이 프로젝트는 학습 및 개발 목적으로 제작되었습니다.

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
