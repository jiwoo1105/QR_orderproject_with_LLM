# ============================================================================
# main.py - FastAPI 메인 서버 파일
# ============================================================================
# 이 파일은 HTTP REST API 서버를 실행하는 메인 파일입니다.
# Spring Boot에서 이 서버의 엔드포인트를 호출하여 AI 챗봇 기능을 사용합니다.
# ============================================================================

# ---------- 라이브러리 임포트 ----------

# FastAPI: Python 웹 프레임워크 (Spring Boot 같은 역할)
# - FastAPI: 웹 애플리케이션 객체
# - HTTPException: 에러 응답을 보내기 위한 클래스
from fastapi import FastAPI, HTTPException

# CORS (Cross-Origin Resource Sharing) 설정
# 다른 도메인(Spring Boot 서버)에서 이 API를 호출할 수 있도록 허용
from fastapi.middleware.cors import CORSMiddleware

# asynccontextmanager: 서버 시작/종료 시 특정 코드를 실행하기 위한 도구
from contextlib import asynccontextmanager

# uvicorn: FastAPI 서버를 실행하는 웹 서버 (Tomcat 같은 역할)
import uvicorn

# models.py에서 데이터 모델(클래스) 임포트
# 각 클래스는 API 요청/응답의 데이터 구조를 정의
from models import (
    ChatRequest,                    # 챗봇 대화 요청 데이터 구조
    ChatResponse,                   # 챗봇 응답 데이터 구조
    MenuRecommendationRequest,      # 메뉴 추천 요청 데이터 구조
    HealthCheckResponse             # 헬스체크 응답 데이터 구조
)

# chatbot_service.py에서 챗봇 클래스 임포트
from chatbot_service import CafeteriaChatbot

# config.py에서 설정 가져오기 함수 임포트
from config import get_settings


# ---------- 전역 변수 ----------

# 챗봇 인스턴스를 전역 변수로 선언
# None으로 초기화하고, 서버 시작 시 실제 객체를 생성
# 왜 전역?: 모든 API 요청에서 같은 챗봇 객체를 재사용 (매번 생성하면 비효율적)
chatbot = None


# ---------- 서버 생명주기 관리 ----------

@asynccontextmanager  # 데코레이터: 이 함수를 컨텍스트 매니저로 만듦
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 이벤트 핸들러

    실행 시점:
    1. 서버 시작 직전 → yield 이전 코드 실행
    2. 서버 종료 직전 → yield 이후 코드 실행

    용도: 데이터베이스 연결, 리소스 초기화, 정리 작업 등
    """
    global chatbot  # 전역 변수 chatbot을 수정하겠다는 선언

    # ===== 서버 시작 시 실행 =====
    # CafeteriaChatbot 객체 생성 (OpenAI 클라이언트 초기화)
    chatbot = CafeteriaChatbot()

    # 터미널에 메시지 출력 (로그)
    print("챗봇 서비스 초기화 완료")

    # yield: 여기서 서버가 실행되고 요청을 처리함
    # yield 이전 = 시작 시, yield 이후 = 종료 시
    yield

    # ===== 서버 종료 시 실행 =====
    # 필요한 정리 작업 (현재는 메시지만 출력)
    print("챗봇 서비스 종료")


# ---------- FastAPI 앱 생성 ----------

# FastAPI 애플리케이션 객체 생성
# 이 객체가 모든 HTTP 요청을 처리함
app = FastAPI(
    # API 문서에 표시될 제목
    title="학식당 챗봇 API",

    # API 문서에 표시될 설명
    description="대학교 학생식당 관리 시스템을 위한 AI 챗봇 API",

    # API 버전 정보
    version="1.0.0",

    # 생명주기 이벤트 핸들러 등록
    # 서버 시작/종료 시 위의 lifespan 함수가 실행됨
    lifespan=lifespan
)


# ---------- CORS 설정 ----------

# CORS (Cross-Origin Resource Sharing) 미들웨어 추가
# 다른 도메인(예: Spring Boot 서버)에서 이 API를 호출할 수 있도록 허용
app.add_middleware(
    CORSMiddleware,  # CORS 처리를 위한 미들웨어 클래스

    # allow_origins: 어떤 도메인에서의 요청을 허용할지 설정
    # ["*"] = 모든 도메인 허용 (개발 환경용)
    # 프로덕션에서는 ["http://localhost:8080", "https://yourdomain.com"] 처럼 구체적으로 지정
    allow_origins=["*"],

    # allow_credentials: 쿠키, 인증 정보 포함 요청 허용 여부
    allow_credentials=True,

    # allow_methods: 허용할 HTTP 메서드
    # ["*"] = 모든 메서드(GET, POST, PUT, DELETE 등) 허용
    allow_methods=["*"],

    # allow_headers: 허용할 HTTP 헤더
    # ["*"] = 모든 헤더 허용
    allow_headers=["*"],
)


# ============================================================================
# API 엔드포인트 정의
# ============================================================================
# 여기서부터 실제 API URL과 처리 함수를 정의합니다.
# @app.get() = GET 요청, @app.post() = POST 요청
# ============================================================================


# ---------- GET / (루트) ----------

@app.get("/", response_model=HealthCheckResponse)
# @app.get: GET 메서드로 "/" 경로에 접근 시 이 함수 실행
# "/": URL 경로 (http://localhost:8000/)
# response_model: 응답 데이터가 HealthCheckResponse 형식임을 명시

async def root():
    """
    루트 엔드포인트 - 서비스 상태 확인

    URL: http://localhost:8000/
    메서드: GET
    용도: 서버가 살아있는지 기본 확인

    호출 예시:
        curl http://localhost:8000/
    """
    # 딕셔너리 반환 → FastAPI가 자동으로 JSON으로 변환
    return {
        "status": "ok",
        "message": "학식당 챗봇 API 서버가 정상 작동 중입니다."
    }
    # 실제 HTTP 응답:
    # HTTP/1.1 200 OK
    # Content-Type: application/json
    #
    # {"status": "ok", "message": "학식당 챗봇 API 서버가 정상 작동 중입니다."}


# ---------- GET /health (헬스체크) ----------

@app.get("/health", response_model=HealthCheckResponse)
# GET 메서드로 "/health" 경로 처리

async def health_check():
    """
    헬스체크 엔드포인트

    URL: http://localhost:8000/health
    메서드: GET
    용도: 서버 상태와 API 키 설정 여부 확인

    호출 예시:
        curl http://localhost:8000/health
    """
    try:
        # config.py에서 설정 정보 가져오기
        settings = get_settings()

        # OpenAI API 키가 설정되어 있는지 확인
        # 삼항 연산자: (조건) ? true_값 : false_값
        api_key_status = "configured" if settings.openai_api_key else "not_configured"

        # 정상 응답 반환
        return {
            "status": "healthy",
            "message": f"API 서버 정상 작동 중 (API Key: {api_key_status})"
        }

    except Exception as e:
        # 에러 발생 시 HTTP 500 에러 응답
        # HTTPException: FastAPI의 에러 처리 클래스
        raise HTTPException(
            status_code=500,  # HTTP 상태 코드 500 (Internal Server Error)
            detail=str(e)     # 에러 메시지
        )


# ---------- POST /chat (메인 챗봇) ----------

@app.post("/chat", response_model=ChatResponse)
# POST 메서드로 "/chat" 경로 처리
# POST: 데이터를 서버에 전송할 때 사용 (요청 본문에 데이터 포함)

async def chat(request: ChatRequest):
    """
    챗봇과 대화하기 (메인 엔드포인트)

    URL: http://localhost:8000/chat
    메서드: POST
    요청 본문: ChatRequest 형식의 JSON

    요청 예시:
        POST http://localhost:8000/chat
        Content-Type: application/json

        {
            "message": "오늘 메뉴 뭐예요?",
            "conversation_history": [...],
            "context": {...}
        }

    Parameters:
        request (ChatRequest): FastAPI가 자동으로 JSON을 ChatRequest 객체로 변환
    """
    try:
        # ===== STEP 1: 대화 히스토리 변환 =====

        # history 변수를 None으로 초기화
        history = None

        # request.conversation_history가 있는지 확인
        # (클라이언트가 이전 대화 기록을 보냈는지)
        if request.conversation_history:
            # 리스트 컴프리헨션으로 데이터 변환
            # Pydantic 모델(Message 객체) → 딕셔너리로 변환
            #
            # request.conversation_history = [
            #     Message(role="user", content="안녕"),
            #     Message(role="assistant", content="안녕하세요")
            # ]
            #
            # 변환 후:
            # history = [
            #     {"role": "user", "content": "안녕"},
            #     {"role": "assistant", "content": "안녕하세요"}
            # ]
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]

        # ===== STEP 2: 챗봇 서비스 호출 =====

        # 전역 변수 chatbot의 chat() 메서드 호출
        # chatbot은 서버 시작 시 생성된 CafeteriaChatbot 객체
        result = chatbot.chat(
            # 사용자가 입력한 질문
            user_message=request.message,

            # 이전 대화 기록 (없으면 None)
            conversation_history=history,

            # 컨텍스트 정보 (메뉴, 운영시간 등, 없으면 None)
            context=request.context
        )

        # result 예시:
        # {
        #     "response": "오늘 메뉴는 김치찌개입니다.",
        #     "model": "gpt-4-turbo-preview",
        #     "tokens_used": 187
        # }

        # ===== STEP 3: 응답 반환 =====

        # **result: 딕셔너리 언패킹
        # ChatResponse(response="...", model="...", tokens_used=187)
        #
        # FastAPI가 자동으로 JSON으로 변환하여 응답
        return ChatResponse(**result)

        # 최종 HTTP 응답:
        # HTTP/1.1 200 OK
        # Content-Type: application/json
        #
        # {
        #     "response": "오늘 메뉴는 김치찌개입니다.",
        #     "model": "gpt-4-turbo-preview",
        #     "tokens_used": 187,
        #     "error": null
        # }

    except Exception as e:
        # 에러 발생 시 HTTP 500 에러 반환
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 처리 중 오류 발생: {str(e)}"
        )


# ---------- POST /recommend (메뉴 추천) ----------

@app.post("/recommend", response_model=ChatResponse)
# POST 메서드로 "/recommend" 경로 처리

async def recommend_menu(request: MenuRecommendationRequest):
    """
    메뉴 추천받기

    URL: http://localhost:8000/recommend
    메서드: POST

    요청 예시:
        POST http://localhost:8000/recommend

        {
            "dietary_restrictions": ["견과류 알레르기"],
            "preferred_cuisine": "한식",
            "budget": 6000,
            "available_menus": [...]
        }
    """
    try:
        # ===== STEP 1: 컨텍스트 구성 =====

        # 빈 딕셔너리 생성
        context = {}

        # 이용 가능한 메뉴가 있으면 컨텍스트에 추가
        if request.available_menus:
            context["menus"] = request.available_menus

        # ===== STEP 2: 추천 프롬프트 생성 =====

        # 프롬프트 문자열 부분들을 담을 리스트
        prompt_parts = ["메뉴를 추천해주세요."]

        # 식이 제한사항이 있으면 추가
        if request.dietary_restrictions:
            # 리스트를 쉼표로 연결
            # ["채식", "견과류"] → "채식, 견과류"
            restrictions = ", ".join(request.dietary_restrictions)
            prompt_parts.append(f"식이 제한사항: {restrictions}")

        # 선호 음식이 있으면 추가
        if request.preferred_cuisine:
            prompt_parts.append(f"선호 음식: {request.preferred_cuisine}")

        # 예산이 있으면 추가
        if request.budget:
            prompt_parts.append(f"예산: {request.budget}원 이하")

        # 모든 부분을 공백으로 연결
        # ["메뉴를 추천해주세요.", "식이 제한사항: 채식", "예산: 6000원 이하"]
        # → "메뉴를 추천해주세요. 식이 제한사항: 채식 예산: 6000원 이하"
        recommendation_message = " ".join(prompt_parts)

        # ===== STEP 3: 챗봇 호출 =====

        # 생성된 프롬프트로 챗봇 호출
        result = chatbot.chat(
            user_message=recommendation_message,
            context=context
            # conversation_history는 생략 (None)
        )

        # ===== STEP 4: 응답 반환 =====
        return ChatResponse(**result)

    except Exception as e:
        # 에러 발생 시 HTTP 500 에러 반환
        raise HTTPException(
            status_code=500,
            detail=f"메뉴 추천 중 오류 발생: {str(e)}"
        )


# ---------- POST /chat/simple (간단한 테스트용) ----------

@app.post("/chat/simple")
# POST 메서드로 "/chat/simple" 경로 처리

async def simple_chat(message: str):
    """
    간단한 챗봇 대화 (테스트용)

    URL: http://localhost:8000/chat/simple?message=안녕하세요
    메서드: POST

    매개변수:
        message (str): 쿼리 파라미터로 전달된 메시지

    주의: 이 엔드포인트는 쿼리 파라미터를 사용
         /chat은 JSON Body를 사용

    호출 예시:
        curl -X POST "http://localhost:8000/chat/simple?message=안녕하세요"
    """
    try:
        # 챗봇 호출 (컨텍스트와 히스토리 없이 메시지만 전달)
        result = chatbot.chat(user_message=message)

        # 딕셔너리를 그대로 반환 (ChatResponse 형식 아님!)
        # {"response": "...", "model": "...", "tokens_used": ...}
        return result

    except Exception as e:
        # 에러 발생 시 HTTP 500 에러 반환
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 처리 중 오류 발생: {str(e)}"
        )


# ============================================================================
# 서버 실행 코드
# ============================================================================

# __name__ == "__main__": 이 파일이 직접 실행되었을 때만 실행
# import로 불러왔을 때는 실행 안 됨
if __name__ == "__main__":
    # config.py에서 설정 정보 가져오기
    settings = get_settings()

    # uvicorn으로 FastAPI 서버 실행
    uvicorn.run(
        # "main:app": main.py 파일의 app 객체를 실행
        # 형식: "파일명:변수명"
        "main:app",

        # host: 서버가 바인딩될 주소
        # "0.0.0.0" = 모든 네트워크 인터페이스에서 접근 가능
        # "127.0.0.1"이면 localhost에서만 접근 가능
        host=settings.host,  # .env 파일에서 설정한 값

        # port: 서버가 사용할 포트 번호
        port=settings.port,  # .env 파일에서 설정한 값 (기본 8000)

        # reload: 코드 변경 시 자동으로 서버 재시작
        # 개발 환경에서만 True, 프로덕션에서는 False
        reload=True
    )

    # 실행 결과:
    # INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    # INFO:     Started reloader process [12345] using StatReload
    # INFO:     Started server process [12346]
    # INFO:     Waiting for application startup.
    # 챗봇 서비스 초기화 완료
    # INFO:     Application startup complete.


# ============================================================================
# 전체 실행 흐름
# ============================================================================
"""
1. python3 main.py 실행

2. FastAPI 앱(app) 생성
   → title, description, version 설정
   → lifespan 이벤트 핸들러 등록

3. CORS 미들웨어 추가
   → 다른 도메인에서 API 호출 가능

4. 모든 엔드포인트(@app.get, @app.post) 등록
   → GET  /
   → GET  /health
   → POST /chat
   → POST /recommend
   → POST /chat/simple

5. uvicorn.run() 실행
   → lifespan 함수의 yield 이전 코드 실행 (챗봇 초기화)
   → 서버 시작, http://0.0.0.0:8000 에서 대기
   → 요청 들어오면 해당 엔드포인트 함수 실행

6. 사용자 요청 처리 예시:
   POST http://localhost:8000/chat
   Body: {"message": "안녕"}

   → chat() 함수 실행
   → chatbot.chat() 호출
   → OpenAI API 호출
   → 응답 생성
   → JSON으로 반환

7. Ctrl+C로 종료 시
   → lifespan 함수의 yield 이후 코드 실행
   → "챗봇 서비스 종료" 출력
   → 서버 종료
"""
