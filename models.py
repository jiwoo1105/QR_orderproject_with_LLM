from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Message(BaseModel):
    """대화 메시지 모델"""
    role: str = Field(..., description="메시지 역할 (user, assistant, system)")
    content: str = Field(..., description="메시지 내용")


class ChatRequest(BaseModel):
    """챗봇 대화 요청 모델"""
    message: str = Field(..., description="사용자 메시지", min_length=1)
    conversation_history: Optional[List[Message]] = Field(
        default=None,
        description="이전 대화 히스토리"
    )
    context: Optional[Dict] = Field(
        default=None,
        description="추가 컨텍스트 (메뉴, 운영시간 등)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "오늘 메뉴가 뭐예요?",
                "conversation_history": [
                    {"role": "user", "content": "안녕하세요"},
                    {"role": "assistant", "content": "안녕하세요! 학생식당 안내 챗봇입니다."}
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
                    
                }
            }
        }


class ChatResponse(BaseModel):
    """챗봇 응답 모델"""
    response: str = Field(..., description="챗봇 응답 메시지")
    model: str = Field(..., description="사용된 AI 모델명")
    tokens_used: int = Field(..., description="사용된 토큰 수")
    error: Optional[str] = Field(default=None, description="에러 메시지 (있는 경우)")


class MenuRecommendationRequest(BaseModel):
    """메뉴 추천 요청 모델"""
    dietary_restrictions: Optional[List[str]] = Field(
        default=None,
        description="식이 제한사항 (예: 채식, 알레르기)"
    )
    preferred_cuisine: Optional[str] = Field(
        default=None,
        description="선호 음식 종류 (한식, 중식, 일식, 양식)"
    )
    budget: Optional[int] = Field(
        default=None,
        description="예산 (원)"
    )
    available_menus: Optional[List[Dict]] = Field(
        default=None,
        description="현재 이용 가능한 메뉴 목록"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "dietary_restrictions": ["견과류 알레르기"],
                "preferred_cuisine": "한식",
                "budget": 6000,
                "available_menus": [
                    {"name": "김치찌개", "price": 5000},
                    {"name": "제육볶음", "price": 5500}
                ]
            }
        }


class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    message: str
