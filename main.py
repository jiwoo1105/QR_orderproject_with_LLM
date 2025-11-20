from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from models import (
    ChatRequest,
    ChatResponse,
    MenuRecommendationRequest,
    HealthCheckResponse
)
from chatbot_service import CafeteriaChatbot
from config import get_settings


# 챗봇 인스턴스를 전역으로 관리
chatbot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 이벤트"""
    global chatbot
    # 시작 시
    chatbot = CafeteriaChatbot()
    print("챗봇 서비스 초기화 완료")
    yield
    # 종료 시
    print("챗봇 서비스 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="학식당 챗봇 API",
    description="대학교 학생식당 관리 시스템을 위한 AI 챗봇 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (Spring Boot 백엔드에서 호출 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """루트 엔드포인트 - 서비스 상태 확인"""
    return {
        "status": "ok",
        "message": "학식당 챗봇 API 서버가 정상 작동 중입니다."
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """헬스체크 엔드포인트"""
    try:
        settings = get_settings()
        api_key_status = "configured" if settings.openai_api_key else "not_configured"
        return {
            "status": "healthy",
            "message": f"API 서버 정상 작동 중 (API Key: {api_key_status})"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    챗봇과 대화하기

    - **message**: 사용자 메시지 (필수)
    - **conversation_history**: 이전 대화 기록 (선택)
    - **context**: 메뉴, 운영시간 등 추가 정보 (선택)
    """
    try:
        # 대화 히스토리를 딕셔너리 리스트로 변환
        history = None
        if request.conversation_history:
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]

        # 챗봇 호출
        result = chatbot.chat(
            user_message=request.message,
            conversation_history=history,
            context=request.context
        )

        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 처리 중 오류 발생: {str(e)}"
        )


@app.post("/recommend", response_model=ChatResponse)
async def recommend_menu(request: MenuRecommendationRequest):
    """
    메뉴 추천받기

    사용자의 선호도와 제약사항을 고려하여 메뉴를 추천합니다.

    - **dietary_restrictions**: 식이 제한사항 (예: 채식, 알레르기)
    - **preferred_cuisine**: 선호 음식 종류
    - **budget**: 예산
    - **available_menus**: 현재 이용 가능한 메뉴
    """
    try:
        # 컨텍스트 구성
        context = {}
        if request.available_menus:
            context["menus"] = request.available_menus

        # 추천 메시지 생성
        prompt_parts = ["메뉴를 추천해주세요."]

        if request.dietary_restrictions:
            restrictions = ", ".join(request.dietary_restrictions)
            prompt_parts.append(f"식이 제한사항: {restrictions}")

        if request.preferred_cuisine:
            prompt_parts.append(f"선호 음식: {request.preferred_cuisine}")

        if request.budget:
            prompt_parts.append(f"예산: {request.budget}원 이하")

        recommendation_message = " ".join(prompt_parts)

        # 챗봇 호출
        result = chatbot.chat(
            user_message=recommendation_message,
            context=context
        )

        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"메뉴 추천 중 오류 발생: {str(e)}"
        )


@app.post("/chat/simple")
async def simple_chat(message: str):
    """
    간단한 챗봇 대화 (쿼리 파라미터)

    테스트용 간단한 엔드포인트
    """
    try:
        result = chatbot.chat(user_message=message)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 처리 중 오류 발생: {str(e)}"
        )


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
