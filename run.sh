#!/bin/bash

# 학식당 챗봇 API 서버 실행 스크립트

echo "학식당 챗봇 API 서버 시작..."

# 가상환경 활성화 (선택사항)
# source venv/bin/activate

# 환경변수 체크
if [ ! -f .env ]; then
    echo "경고: .env 파일이 없습니다. .env.example을 복사하여 .env 파일을 생성하고 API 키를 설정하세요."
    exit 1
fi

# FastAPI 서버 실행
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
