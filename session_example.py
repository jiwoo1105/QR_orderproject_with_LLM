"""
세션 관리가 추가된 FastAPI 예시 코드
실제 사용 시 Redis나 DB로 저장하는 것을 권장
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid

app = FastAPI()

# ===== 메모리에 세션 저장 (테스트용) =====
# 실제 운영에서는 Redis나 DB 사용 권장
sessions = {}

class ChatRequest(BaseModel):
    user_id: str  # ← 사용자 ID 추가
    message: str
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    session_id: str  # ← 세션 ID 반환
    response: str
    model: str
    tokens_used: int

# ===== 세션 관리 클래스 =====
class SessionManager:
    def __init__(self):
        self.sessions = {}  # {session_id: {"history": [...], "last_access": datetime}}

    def get_or_create_session(self, user_id: str) -> str:
        """사용자의 세션 ID 가져오기 또는 생성"""
        # 기존 세션 찾기
        for session_id, data in self.sessions.items():
            if data.get("user_id") == user_id:
                # 30분 이내면 기존 세션 사용
                if datetime.now() - data["last_access"] < timedelta(minutes=30):
                    return session_id

        # 새 세션 생성
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "history": [],
            "last_access": datetime.now()
        }
        return session_id

    def add_message(self, session_id: str, role: str, content: str):
        """대화 기록 추가"""
        if session_id in self.sessions:
            self.sessions[session_id]["history"].append({
                "role": role,
                "content": content
            })
            self.sessions[session_id]["last_access"] = datetime.now()

    def get_history(self, session_id: str) -> List[Dict]:
        """대화 기록 가져오기"""
        if session_id in self.sessions:
            return self.sessions[session_id]["history"]
        return []

    def clear_session(self, session_id: str):
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]

# 전역 세션 매니저
session_manager = SessionManager()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    세션 기반 챗봇 대화

    사용자 ID를 기반으로 세션을 관리하여 대화 기록 유지
    """
    try:
        # 1. 사용자 세션 가져오기 or 생성
        session_id = session_manager.get_or_create_session(request.user_id)

        # 2. 이전 대화 기록 가져오기
        history = session_manager.get_history(session_id)

        # 3. AI 챗봇 호출 (기존 chatbot 사용)
        result = chatbot.chat(
            user_message=request.message,
            conversation_history=history,  # ← 세션에서 가져온 기록
            context=request.context
        )

        # 4. 대화 기록에 추가
        session_manager.add_message(session_id, "user", request.message)
        session_manager.add_message(session_id, "assistant", result["response"])

        # 5. 응답 반환
        return ChatResponse(
            session_id=session_id,  # 세션 ID 포함
            **result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """
    세션 삭제 (대화 초기화)
    """
    session_manager.clear_session(session_id)
    return {"message": "Session cleared"}

# ===== 사용 예시 =====
"""
# 첫 번째 요청
POST /chat
{
  "user_id": "student123",
  "message": "안녕하세요"
}

Response:
{
  "session_id": "abc-123-def",
  "response": "안녕하세요! 무엇을 도와드릴까요?",
  "model": "gpt-4",
  "tokens_used": 50
}

# 두 번째 요청 (같은 user_id)
POST /chat
{
  "user_id": "student123",  # ← 같은 사용자
  "message": "메뉴 뭐예요?"
}

Response:
{
  "session_id": "abc-123-def",  # ← 같은 세션
  "response": "메뉴는 김치찌개와 제육볶음입니다.",
  "model": "gpt-4",
  "tokens_used": 70
}

# AI는 이전 대화("안녕하세요")를 기억함!
"""
