import asyncio
import signal
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from config import settings
from slack.event_handler import app as slack_app

async def main():
    # 시그널 핸들러 설정
    loop = asyncio.get_running_loop()
    stop = asyncio.Event()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    
    # Slack 핸들러 설정
    slack_handler = AsyncSocketModeHandler(
        app=slack_app,
        app_token=settings.SLACK_APP_TOKEN,
    )
    
    # 연결 시작
    await slack_handler.connect_async()
    print("Slack Socket Mode 연결 성공")
    
    try:
        # 종료 시그널을 기다림
        await stop.wait()
    finally:
        # 깔끔한 종료 처리
        await slack_handler.close_async()
        print("Slack Socket Mode 연결 종료")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")