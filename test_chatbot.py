"""
챗봇 API 테스트 스크립트

서버가 실행 중이어야 합니다: python main.py
"""

import requests
import json


BASE_URL = "http://localhost:8000"


def test_health_check():
    """헬스체크 테스트"""
    print("\n=== 헬스체크 테스트 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_simple_chat():
    """간단한 대화 테스트"""
    print("\n=== 간단한 대화 테스트 ===")
    message = "안녕하세요! 학생식당에 대해 알려주세요."
    response = requests.post(
        f"{BASE_URL}/chat/simple",
        params={"message": message}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_chat_with_context():
    """컨텍스트가 포함된 대화 테스트"""
    print("\n=== 컨텍스트 포함 대화 테스트 ===")

    payload = {
        "message": "오늘 메뉴 중에 뭐가 맛있어요?",
        "context": {
            "menus": [
                {
                    "name": "김치찌개",
                    "price": 5000,
                    "calories": 450,
                    "description": "얼큰한 국내산 김치로 만든 찌개"
                },
                {
                    "name": "제육볶음",
                    "price": 5500,
                    "calories": 520,
                    "description": "매콤달콤한 제육볶음"
                },
                {
                    "name": "된장찌개",
                    "price": 4500,
                    "calories": 380,
                    "description": "구수한 된장찌개"
                }
            ],
            "operating_hours": {
                "조식": "08:00 - 09:30",
                "중식": "11:30 - 13:30",
                "석식": "17:30 - 19:00"
            },
            "location": "학생회관 1층 학생식당"
        }
    }

    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_chat_with_history():
    """대화 히스토리 포함 테스트"""
    print("\n=== 대화 히스토리 포함 테스트 ===")

    payload = {
        "message": "그럼 그 메뉴의 가격은 얼마인가요?",
        "conversation_history": [
            {
                "role": "user",
                "content": "오늘 메뉴 뭐 있어요?"
            },
            {
                "role": "assistant",
                "content": "오늘은 김치찌개, 제육볶음, 된장찌개가 있습니다."
            },
            {
                "role": "user",
                "content": "김치찌개 추천해주세요"
            },
            {
                "role": "assistant",
                "content": "김치찌개 좋은 선택이십니다! 얼큰한 국내산 김치로 만들어 맛이 좋습니다."
            }
        ],
        "context": {
            "menus": [
                {"name": "김치찌개", "price": 5000, "calories": 450},
                {"name": "제육볶음", "price": 5500, "calories": 520},
                {"name": "된장찌개", "price": 4500, "calories": 380}
            ]
        }
    }

    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_menu_recommendation():
    """메뉴 추천 테스트"""
    print("\n=== 메뉴 추천 테스트 ===")

    payload = {
        "dietary_restrictions": ["견과류 알레르기"],
        "preferred_cuisine": "한식",
        "budget": 5500,
        "available_menus": [
            {"name": "김치찌개", "price": 5000, "calories": 450},
            {"name": "제육볶음", "price": 5500, "calories": 520},
            {"name": "샐러드", "price": 6000, "calories": 250, "note": "견과류 포함"},
            {"name": "된장찌개", "price": 4500, "calories": 380}
        ]
    }

    response = requests.post(
        f"{BASE_URL}/recommend",
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("학식당 챗봇 API 테스트 시작")
    print("=" * 60)

    try:
        test_health_check()
        test_simple_chat()
        test_chat_with_context()
        test_chat_with_history()
        test_menu_recommendation()

        print("\n" + "=" * 60)
        print("모든 테스트 완료!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ 오류: 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: python main.py")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
