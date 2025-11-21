# 학식당 챗봇 API 배포 가이드

## Docker 이미지 파일
- 파일명: `cafeteria-chatbot.tar`
- 크기: 약 53MB
- 이미지명: `cafeteria-chatbot:latest`

## 배포 서버에서 실행하기

### 1. Docker 이미지 로드
```bash
docker load -i cafeteria-chatbot.tar
```

### 2. 환경 변수 설정
실제 운영 환경에 맞게 환경 변수를 설정하세요.

```bash
# .env 파일 생성
cat > .env << EOF
OPENAI_API_KEY=실제_OpenAI_API_키
HOST=0.0.0.0
PORT=8000
MODEL_NAME=gpt-4-turbo-preview
MAX_TOKENS=1000
TEMPERATURE=0.7
EOF
```

### 3. Docker 컨테이너 실행

#### 방법 1: 환경 변수 파일 사용
```bash
docker run -d \
  --name cafeteria-chatbot \
  -p 8000:8000 \
  --env-file .env \
  cafeteria-chatbot:latest
```

#### 방법 2: 직접 환경 변수 전달
```bash
docker run -d \
  --name cafeteria-chatbot \
  -p 8000:8000 \
  -e OPENAI_API_KEY=실제_OpenAI_API_키 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e MODEL_NAME=gpt-4-turbo-preview \
  -e MAX_TOKENS=1000 \
  -e TEMPERATURE=0.7 \
  cafeteria-chatbot:latest
```

### 4. 컨테이너 상태 확인
```bash
# 실행 중인 컨테이너 확인
docker ps

# 로그 확인
docker logs cafeteria-chatbot

# 실시간 로그 확인
docker logs -f cafeteria-chatbot
```

### 5. 헬스체크
```bash
curl http://localhost:8000/health
```

예상 응답:
```json
{
  "status": "healthy",
  "message": "API 서버 정상 작동 중 (API Key: configured)"
}
```

## 컨테이너 관리 명령어

### 컨테이너 중지
```bash
docker stop cafeteria-chatbot
```

### 컨테이너 시작
```bash
docker start cafeteria-chatbot
```

### 컨테이너 재시작
```bash
docker restart cafeteria-chatbot
```

### 컨테이너 삭제
```bash
docker rm -f cafeteria-chatbot
```

## Spring Boot 연동

### 1. Spring Boot application.yml 설정
```yaml
chatbot:
  api:
    url: http://localhost:8000
    # 또는 실제 배포 서버 주소
    # url: http://192.168.1.100:8000
```

### 2. Spring Boot에서 API 호출 예제
```java
@Service
public class ChatbotService {

    @Value("${chatbot.api.url}")
    private String chatbotApiUrl;

    private final RestTemplate restTemplate;

    public String chat(String userMessage, List<Message> previousMessages, List<Menu> menus) {
        String url = chatbotApiUrl + "/chat";

        Map<String, Object> request = new HashMap<>();
        request.put("message", userMessage);
        request.put("previousMessages", previousMessages);
        request.put("menus", menus);

        ResponseEntity<ChatResponse> response = restTemplate.postForEntity(
            url,
            request,
            ChatResponse.class
        );

        return response.getBody().getMessage();
    }
}

// 응답 DTO
@Data
public class ChatResponse {
    private String message;
}
```

## 프로덕션 배포 시 고려사항

### 1. 포트 변경
기본 포트 8000 대신 다른 포트 사용 시:
```bash
docker run -d \
  --name cafeteria-chatbot \
  -p 9000:8000 \
  --env-file .env \
  cafeteria-chatbot:latest
```

### 2. 네트워크 설정
Spring Boot 컨테이너와 같은 네트워크 사용 시:
```bash
# 네트워크 생성
docker network create app-network

# 챗봇 컨테이너 실행
docker run -d \
  --name cafeteria-chatbot \
  --network app-network \
  -p 8000:8000 \
  --env-file .env \
  cafeteria-chatbot:latest

# Spring Boot에서는 http://cafeteria-chatbot:8000 으로 접근
```

### 3. 리소스 제한
```bash
docker run -d \
  --name cafeteria-chatbot \
  -p 8000:8000 \
  --memory="512m" \
  --cpus="1.0" \
  --env-file .env \
  cafeteria-chatbot:latest
```

### 4. 자동 재시작 설정
```bash
docker run -d \
  --name cafeteria-chatbot \
  -p 8000:8000 \
  --restart unless-stopped \
  --env-file .env \
  cafeteria-chatbot:latest
```

## Docker Compose 사용 (선택사항)

`docker-compose.yml` 파일 생성:
```yaml
version: '3.8'

services:
  chatbot:
    image: cafeteria-chatbot:latest
    container_name: cafeteria-chatbot
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HOST=0.0.0.0
      - PORT=8000
      - MODEL_NAME=gpt-4-turbo-preview
      - MAX_TOKENS=1000
      - TEMPERATURE=0.7
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

실행:
```bash
docker-compose up -d
```

## 문제 해결

### API 키 오류
```
Error code: 401 - Invalid API key
```
→ 환경 변수 OPENAI_API_KEY 확인

### 포트 충돌
```
Error: port is already allocated
```
→ 다른 포트 사용: `-p 9000:8000`

### 컨테이너 실행 실패
```bash
# 상세 로그 확인
docker logs cafeteria-chatbot

# 컨테이너 내부 접속
docker exec -it cafeteria-chatbot /bin/bash
```

## API 엔드포인트

### 1. 헬스체크
```
GET /health
```

### 2. 챗봇 대화
```
POST /chat
```

요청:
```json
{
  "message": "오늘 메뉴가 뭐예요?",
  "previousMessages": [
    {"role": "USER", "content": "안녕하세요"},
    {"role": "ASSISTANT", "content": "안녕하세요!"}
  ],
  "menus": [
    {
      "name": "김치찌개",
      "price": 5000,
      "restaurantName": "학생식당 1관",
      "nutritionInfo": {
        "calories": 450,
        "protein": 25.5,
        "fat": 15.2,
        "carbs": 48.0,
        "sodium": 980
      },
      "allergyIngredients": ["대두", "돼지고기"]
    }
  ]
}
```

응답:
```json
{
  "message": "오늘 메뉴는 김치찌개가 있습니다. 5,000원이며..."
}
```

### 3. 메뉴 추천
```
POST /recommend
```

요청:
```json
{
  "dietary_restrictions": ["견과류 알레르기"],
  "preferred_cuisine": "한식",
  "budget": 6000,
  "available_menus": [...]
}
```

## 보안 고려사항

1. `.env` 파일은 절대 Git에 커밋하지 마세요
2. API 키는 환경 변수로만 관리하세요
3. 프로덕션에서는 HTTPS 사용을 권장합니다
4. CORS 설정을 필요한 도메인만 허용하도록 수정하세요

## 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
