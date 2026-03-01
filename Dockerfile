# 1. 베이스 이미지 (파이썬 3.11이 깔린 가벼운 리눅스 환경을 가져옴)
FROM python:3.12-slim

# 2. 작업 폴더 설정 (컨테이너 내부의 /app 이라는 폴더에서 작업하겠다)
WORKDIR /app

# 3. 필요한 라이브러리 설치를 위해 requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# 4. 내 파이썬 코드들(sqlagent.py 등)을 컨테이너 안으로 복사
COPY . .

# 5. FastAPI 서버 실행 명령어 (임베디드의 main() 함수 진입점 같은 역할)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]