서강대학교 AI_MBA 5기 SummerAI(Alba B team) 인공지능 응용실습 프로젝트 입니다. 

# 구동방법 

## 1. 소스 내려받기 

    git clone https://github.com/ppillip/summerAI.git

## 2. 폴더로 이동

    cd summerAI

## 3. 의존성 패키지 설치

    pip install -r requirements.txt

## 4. .env 파일 수정 
몽고디비 관련 설정을 수정합니다. 

    DB_USERNAME=사용자명

    DB_PASSWORD=패스워드

    DB_HOST=호스트명 (보통은 도메인 또는 ip) 

    DB_NAME=mimi (이거는 그냥 두세요)

보내는 메일 서버 설정을 수정합니다. 

    SMTP_SERVER=smtp.naver.com (네이버입니다)

    SMTP_USER_ID=보내는 메일 주소

    SMTP_USER_PW=보내는 메일 비밀 번호

    SMTP_PORT=587 (포트입니다)


## 5. 콘솔에서 실행

    python app.py


![summerAI](https://github.com/user-attachments/assets/7b7d0063-4a21-4b15-b446-92587eba3be0)