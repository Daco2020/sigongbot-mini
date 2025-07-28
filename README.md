# 시공봇 로컬 실행 방법

### 1. Python 환경 진입

### 2. 패키지 설치
아래 명령어를 통해 필요한 패키지를 설치합니다.
```zsh
pip install -r requirements.txt
```

### 3. 환경 변수 입력
3-1. 루트 경로에 `.env` 파일을 생성합니다.

3-2. `.env` 파일에 아래 환경 변수를 입력해주세요.
```zsh
ENV=...
SLACK_BOT_TOKEN=...
SLACK_APP_TOKEN=...
ADMIN_CHANNEL=...
SUPPORT_CHANNEL=...
ADMIN_IDS=...
SUPABASE_URL=...
SUPABASE_KEY=...
```

### 4. 시공봇 서버 실행
아래 명령어를 통해 SlackBolt 서버를 실행합니다.
```zsh
python main.py
```

<br><br>

# 시공봇 배포 방법

아래 유튜브 영상 참고

👉 [무료로 서버 배포하는 방법 (Koyeb으로 5분 만에 배포)](https://youtu.be/Rhp911TB0lo)
