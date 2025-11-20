from openai import OpenAI
from typing import List, Dict, Optional
from config import get_settings


class CafeteriaChatbot:
    """학식당 관리 시스템 챗봇 서비스"""

    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.model_name
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature

        # 학식당 챗봇 시스템 프롬프트
        self.system_prompt = """
당신은 대학교 학생식당 관리 시스템의 친절한 AI 어시스턴트입니다.

역할:
- 학생식당의 메뉴, 영양정보, 운영시간 등에 대해 안내합니다
- 사용자의 질문에 정확하고 친절하게 답변합니다
- 메뉴 추천, 식단 정보, 예약 관련 도움을 제공합니다

응답 가이드라인:
1. 간결하고 명확하게 답변하세요
2. 한국어로 친근하게 대화하세요
3. 정보가 불확실하면 솔직히 말하고 관리자에게 문의하도록 안내하세요
4. 메뉴나 시간 정보는 정확하게 전달하세요
"""

    def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        챗봇과 대화하기

        Args:
            user_message: 사용자 메시지
            conversation_history: 이전 대화 히스토리 [{"role": "user", "content": "..."}, ...]
            context: 추가 컨텍스트 (메뉴 정보, 운영시간 등)

        Returns:
            Dict: {
                "response": "챗봇 응답 메시지",
                "model": "사용된 모델명",
                "tokens_used": 사용된 토큰 수
            }
        """
        try:
            # 메시지 구성
            messages = [{"role": "system", "content": self.system_prompt}]

            # 컨텍스트가 있으면 시스템 메시지에 추가
            if context:
                context_message = self._format_context(context)
                messages.append({
                    "role": "system",
                    "content": f"현재 이용 가능한 정보:\n{context_message}"
                })

            # 대화 히스토리 추가
            if conversation_history:
                messages.extend(conversation_history)

            # 현재 사용자 메시지 추가
            messages.append({"role": "user", "content": user_message})

            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return {
                "response": response.choices[0].message.content,
                "model": self.model_name,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            return {
                "response": f"죄송합니다. 일시적인 오류가 발생했습니다: {str(e)}",
                "model": self.model_name,
                "tokens_used": 0,
                "error": str(e)
            }

    def _format_context(self, context: Dict) -> str:
        """컨텍스트 정보를 포맷팅"""
        formatted = []

        if "menus" in context:
            formatted.append("=== 오늘의 메뉴 ===")
            for menu in context["menus"]:
                menu_info = f"- {menu.get('name', 'N/A')}"
                if "price" in menu:
                    menu_info += f" ({menu['price']}원)"
                if "calories" in menu:
                    menu_info += f" | {menu['calories']}kcal"
                formatted.append(menu_info)

        if "operating_hours" in context:
            formatted.append("\n=== 운영 시간 ===")
            for key, value in context["operating_hours"].items():
                formatted.append(f"- {key}: {value}")

        if "location" in context:
            formatted.append(f"\n=== 위치 ===\n- {context['location']}")

        if "announcements" in context:
            formatted.append("\n=== 공지사항 ===")
            for announcement in context["announcements"]:
                formatted.append(f"- {announcement}")

        return "\n".join(formatted)

    def generate_menu_recommendation(self, preferences: Dict) -> Dict:
        """
        사용자 선호도 기반 메뉴 추천

        Args:
            preferences: 사용자 선호도 정보
                {
                    "dietary_restrictions": ["채식", "견과류 알레르기"],
                    "preferred_cuisine": "한식",
                    "budget": 6000
                }
        """
        prompt = f"""
다음 사용자 선호도를 고려하여 오늘의 메뉴 중 가장 적합한 메뉴를 추천해주세요:

{self._format_context(preferences)}

추천 이유도 함께 설명해주세요.
"""
        return self.chat(prompt)
