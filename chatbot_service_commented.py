# ============================================================================
# chatbot_service.py - 학식당 챗봇 핵심 로직
# ============================================================================
# 이 파일은 ChatGPT API와 통신하여 사용자 질문에 답변하는 핵심 비즈니스 로직입니다.
# ============================================================================

# ---------- 라이브러리 임포트 ----------
from openai import OpenAI  # OpenAI의 ChatGPT API를 사용하기 위한 클라이언트
from typing import List, Dict, Optional  # 타입 힌트용 (코드의 가독성과 안정성 향상)
from config import get_settings  # 설정 파일에서 API 키 등의 설정 가져오기


class CafeteriaChatbot:
    """
    학식당 관리 시스템 챗봇 서비스 클래스

    역할: ChatGPT API를 사용하여 학식당 관련 질문에 답변하는 챗봇
    """

    def __init__(self):
        """
        챗봇 초기화 메서드
        객체가 생성될 때 한 번만 실행됩니다.
        """
        # ① config.py에서 설정 정보 가져오기 (.env 파일의 내용)
        settings = get_settings()

        # ② OpenAI 클라이언트 생성 (ChatGPT API와 통신하는 객체)
        # api_key: .env 파일에 저장된 OpenAI API 키 사용
        self.client = OpenAI(api_key=settings.openai_api_key)

        # ③ 사용할 AI 모델 이름 저장 (예: "gpt-4-turbo-preview")
        self.model_name = settings.model_name

        # ④ 최대 토큰 수 (AI가 생성할 수 있는 최대 글자 수)
        # 1000 토큰 ≈ 750 단어 ≈ 500자 정도
        self.max_tokens = settings.max_tokens

        # ⑤ Temperature (AI 답변의 창의성 조절)
        # 0에 가까우면 → 정확하고 일관된 답변
        # 1에 가까우면 → 창의적이고 다양한 답변
        # 0.7 = 균형잡힌 값
        self.temperature = settings.temperature

        # ⑥ 시스템 프롬프트 (AI의 역할과 행동 방식 정의)
        # 이것이 AI에게 "당신은 학식당 어시스턴트입니다"라고 학습시키는 부분!
        self.system_prompt = """
당신은 대학교 학생식당 관리 시스템의 친절한 AI 어시스턴트입니다.

역할:
- 학생식당의 메뉴, 영양정보,운영시간 등에 대해 안내합니다
- 사용자의 질문에 정확하고 친절하게 답변합니다
- 메뉴 추천, 식단 정보 관련 도움을 제공합니다

응답 가이드라인:
1. 간결하고 명확하게 답변하세요
2. 한국어로 친근하게 대화하세요
3. 정보가 불확실하면 솔직히 말하고 관리자에게 문의하도록 안내하세요
4. 메뉴나 시간 정보는 정확하게 전달하세요
"""

    def chat(
        self,
        user_message: str,  # 사용자가 입력한 질문 (예: "오늘 메뉴 뭐예요?")
        conversation_history: Optional[List[Dict[str, str]]] = None,  # 이전 대화 기록 (선택사항)
        context: Optional[Dict] = None  # 메뉴, 운영시간 등 추가 정보 (선택사항)
    ) -> Dict:  # 반환값: AI 답변이 담긴 딕셔너리
        """
        챗봇과 대화하는 메인 함수

        동작 순서:
        1. 시스템 프롬프트 준비 (AI 역할 정의)
        2. 컨텍스트 추가 (메뉴 정보 등)
        3. 대화 히스토리 추가 (이전 대화)
        4. 사용자 질문 추가
        5. OpenAI API 호출
        6. 응답 반환

        Args:
            user_message: 사용자 메시지 (예: "오늘 메뉴 뭐예요?")
            conversation_history: 이전 대화 히스토리
                [
                    {"role": "user", "content": "안녕"},
                    {"role": "assistant", "content": "안녕하세요!"}
                ]
            context: 추가 컨텍스트 (메뉴 정보, 운영시간 등)
                {
                    "menus": [{"name": "김치찌개", "price": 5000}],
                    "operating_hours": {"중식": "11:30-13:30"}
                }

        Returns:
            Dict: {
                "response": "챗봇 응답 메시지",
                "model": "사용된 모델명",
                "tokens_used": 사용된 토큰 수
            }
        """
        try:
            # ========== STEP 1: 메시지 배열 초기화 ==========
            # OpenAI API에 보낼 메시지들을 담는 리스트
            # 첫 번째로 시스템 프롬프트를 추가 (AI의 역할 정의)
            messages = [{"role": "system", "content": self.system_prompt}]

            # 현재 상태: messages = [
            #     {"role": "system", "content": "당신은 학식당 AI 어시스턴트입니다..."}
            # ]

            # ========== STEP 2: 컨텍스트 추가 (있는 경우) ==========
            # context가 전달되었는지 확인
            if context:
                # _format_context() 메서드를 호출하여 context를 읽기 쉬운 텍스트로 변환
                # 예: {"menus": [...]} → "=== 오늘의 메뉴 ===\n- 김치찌개 (5000원)\n..."
                context_message = self._format_context(context)

                # 변환된 컨텍스트를 시스템 메시지로 추가
                # AI에게 "현재 이용 가능한 메뉴는 이렇습니다"라고 알려주는 부분
                messages.append({
                    "role": "system",  # 시스템 메시지 (AI에게 정보 제공)
                    "content": f"현재 이용 가능한 정보:\n{context_message}"
                })

            # 현재 상태: messages = [
            #     {"role": "system", "content": "당신은 학식당 AI..."},
            #     {"role": "system", "content": "현재 이용 가능한 정보:\n=== 오늘의 메뉴 ===\n..."}
            # ]

            # ========== STEP 3: 대화 히스토리 추가 (있는 경우) ==========
            # 이전 대화 기록이 있으면 추가
            # 예: 사용자가 "안녕" → AI "안녕하세요" → 사용자 "메뉴 뭐예요?"
            # 이렇게 이어지는 대화를 위해 이전 대화를 AI에게 알려줌
            if conversation_history:
                # extend()는 리스트의 모든 요소를 추가
                # conversation_history = [
                #     {"role": "user", "content": "안녕"},
                #     {"role": "assistant", "content": "안녕하세요"}
                # ]
                messages.extend(conversation_history)

            # 현재 상태: messages = [
            #     {"role": "system", "content": "당신은 학식당 AI..."},
            #     {"role": "system", "content": "=== 오늘의 메뉴 ===\n..."},
            #     {"role": "user", "content": "안녕"},
            #     {"role": "assistant", "content": "안녕하세요"}
            # ]

            # ========== STEP 4: 현재 사용자 메시지 추가 ==========
            # 사용자가 지금 입력한 질문을 추가
            # 예: "오늘 메뉴 뭐예요?"
            messages.append({"role": "user", "content": user_message})

            # 최종 상태: messages = [
            #     {"role": "system", "content": "당신은 학식당 AI..."},
            #     {"role": "system", "content": "=== 오늘의 메뉴 ===\n..."},
            #     {"role": "user", "content": "안녕"},
            #     {"role": "assistant", "content": "안녕하세요"},
            #     {"role": "user", "content": "오늘 메뉴 뭐예요?"}
            # ]

            # ========== STEP 5: OpenAI API 호출 ==========
            # 준비된 messages를 OpenAI 서버로 전송
            # self.client.chat.completions.create() = ChatGPT API 호출 함수
            response = self.client.chat.completions.create(
                model=self.model_name,      # 사용할 모델 (예: "gpt-4-turbo-preview")
                messages=messages,           # 위에서 준비한 메시지 배열
                max_tokens=self.max_tokens,  # 최대 생성 토큰 수 (1000)
                temperature=self.temperature # 창의성 수준 (0.7)
            )

            # OpenAI 서버 처리 과정:
            # 1. messages 받음
            # 2. GPT-4 모델 로드
            # 3. 시스템 프롬프트 + 컨텍스트 + 대화 히스토리 + 질문 분석
            # 4. 최적의 답변 생성
            # 5. response 객체로 반환

            # response 객체 구조:
            # response = {
            #     choices: [
            #         {
            #             message: {
            #                 content: "오늘 메뉴는 김치찌개와 제육볶음입니다..."
            #             }
            #         }
            #     ],
            #     usage: {
            #         total_tokens: 187
            #     }
            # }

            # ========== STEP 6: 응답 데이터 구성 및 반환 ==========
            # OpenAI로부터 받은 응답을 정리해서 딕셔너리로 반환
            return {
                # AI가 생성한 답변 텍스트
                # response.choices[0] = 첫 번째 답변 선택지
                # .message.content = 실제 답변 내용
                "response": response.choices[0].message.content,

                # 사용된 AI 모델 이름
                "model": self.model_name,

                # 이번 대화에서 사용된 총 토큰 수
                # 토큰 = OpenAI의 과금 단위 (토큰 많이 쓸수록 비용 증가)
                "tokens_used": response.usage.total_tokens
            }

        # ========== 에러 처리 ==========
        # API 호출 중 에러 발생 시 (네트워크 오류, API 키 문제 등)
        except Exception as e:
            # 에러가 발생해도 프로그램이 죽지 않도록 에러 메시지 반환
            return {
                "response": f"죄송합니다. 일시적인 오류가 발생했습니다: {str(e)}",
                "model": self.model_name,
                "tokens_used": 0,  # 에러 발생 시 토큰 사용 없음
                "error": str(e)    # 에러 내용 저장
            }

    def _format_context(self, context: Dict) -> str:
        """
        컨텍스트 정보를 AI가 이해하기 쉬운 텍스트로 변환

        입력 예시:
        {
            "menus": [
                {"name": "김치찌개", "price": 5000, "calories": 450}
            ],
            "operating_hours": {
                "조식": "08:00-09:30"
            },
            "location": "학생회관 1층"
        }

        출력 예시:
        === 오늘의 메뉴 ===
        - 김치찌개 (5000원) | 450kcal

        === 운영 시간 ===
        - 조식: 08:00-09:30

        === 위치 ===
        - 학생회관 1층
        """
        # 포맷팅된 텍스트를 담을 리스트
        formatted = []

        # ========== 메뉴 정보 포맷팅 ==========
        # context에 "menus" 키가 있는지 확인
        if "menus" in context:
            # 섹션 제목 추가
            formatted.append("=== 오늘의 메뉴 ===")

            # 각 메뉴를 순회하면서 포맷팅
            # context["menus"] = [
            #     {"name": "김치찌개", "price": 5000, "calories": 450},
            #     {"name": "제육볶음", "price": 5500, "calories": 520}
            # ]
            for menu in context["menus"]:
                # 메뉴 이름 가져오기 (없으면 "N/A")
                # menu.get("name", "N/A") = menu 딕셔너리에서 "name" 키의 값 가져오기
                menu_info = f"- {menu.get('name', 'N/A')}"

                # 가격 정보가 있으면 추가
                if "price" in menu:
                    menu_info += f" ({menu['price']}원)"

                # 칼로리 정보가 있으면 추가
                if "calories" in menu:
                    menu_info += f" | {menu['calories']}kcal"

                # 완성된 메뉴 정보를 리스트에 추가
                # 예: "- 김치찌개 (5000원) | 450kcal"
                formatted.append(menu_info)

        # ========== 운영 시간 포맷팅 ==========
        # context에 "operating_hours" 키가 있는지 확인
        if "operating_hours" in context:
            # 섹션 제목 추가 (앞에 줄바꿈 추가로 섹션 구분)
            formatted.append("\n=== 운영 시간 ===")

            # 운영시간 딕셔너리를 순회
            # context["operating_hours"] = {
            #     "조식": "08:00 - 09:30",
            #     "중식": "11:30 - 13:30"
            # }
            for key, value in context["operating_hours"].items():
                # 예: "- 조식: 08:00 - 09:30"
                formatted.append(f"- {key}: {value}")

        # ========== 위치 정보 포맷팅 ==========
        # context에 "location" 키가 있는지 확인
        if "location" in context:
            # 위치 정보 추가
            # 예: "=== 위치 ===\n- 학생회관 1층"
            formatted.append(f"\n=== 위치 ===\n- {context['location']}")

        # ========== 공지사항 포맷팅 ==========
        # context에 "announcements" 키가 있는지 확인
        if "announcements" in context:
            # 섹션 제목 추가
            formatted.append("\n=== 공지사항 ===")

            # 공지사항 리스트 순회
            # context["announcements"] = [
            #     "내일은 점심 운영 안 함",
            #     "다음주 월요일 휴무"
            # ]
            for announcement in context["announcements"]:
                # 각 공지사항 앞에 "- " 붙여서 추가
                formatted.append(f"- {announcement}")

        # ========== 최종 텍스트 생성 ==========
        # 리스트의 모든 문자열을 줄바꿈(\n)으로 연결
        # formatted = [
        #     "=== 오늘의 메뉴 ===",
        #     "- 김치찌개 (5000원) | 450kcal",
        #     "\n=== 운영 시간 ===",
        #     "- 조식: 08:00 - 09:30"
        # ]
        #
        # "\n".join(formatted) 결과:
        # """
        # === 오늘의 메뉴 ===
        # - 김치찌개 (5000원) | 450kcal
        #
        # === 운영 시간 ===
        # - 조식: 08:00 - 09:30
        # """
        return "\n".join(formatted)

    def generate_menu_recommendation(self, preferences: Dict) -> Dict:
        """
        사용자 선호도를 기반으로 메뉴를 추천하는 함수

        Args:
            preferences: 사용자 선호도 정보
                {
                    "dietary_restrictions": ["채식", "견과류 알레르기"],
                    "preferred_cuisine": "한식",
                    "budget": 6000
                }

        Returns:
            chat() 메서드와 동일한 형식의 딕셔너리
        """
        # 추천 요청 프롬프트 생성
        # f-string을 사용하여 선호도 정보를 포함한 질문 생성
        prompt = f"""
다음 사용자 선호도를 고려하여 오늘의 메뉴 중 가장 적합한 메뉴를 추천해주세요:

{self._format_context(preferences)}

추천 이유도 함께 설명해주세요.
"""
        # chat() 메서드를 재사용하여 추천 요청
        # 내부적으로 OpenAI API 호출하여 답변 생성
        return self.chat(prompt)


# ============================================================================
# 전체 동작 흐름 정리
# ============================================================================
"""
1. 챗봇 객체 생성:
   chatbot = CafeteriaChatbot()
   → __init__() 실행
   → OpenAI 클라이언트 초기화
   → 시스템 프롬프트 준비

2. 사용자 질문 처리:
   result = chatbot.chat(
       user_message="오늘 메뉴 뭐예요?",
       context={"menus": [...]},
       conversation_history=[...]
   )

   → chat() 메서드 실행
   → messages 배열 구성:
      [
          {"role": "system", "content": "당신은 학식당 AI..."},
          {"role": "system", "content": "=== 오늘의 메뉴 ===..."},
          {"role": "user", "content": "안녕"},
          {"role": "assistant", "content": "안녕하세요"},
          {"role": "user", "content": "오늘 메뉴 뭐예요?"}
      ]
   → OpenAI API 호출
   → 응답 받기
   → 결과 반환

3. 결과 사용:
   print(result["response"])
   # "오늘 메뉴는 김치찌개(5,000원)와 제육볶음(5,500원)입니다!"
"""
