import asyncio
import os
import aiohttp
from aiohttp import web
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from config import settings
from slack.event_handler import app as slack_app

async def health_check(request):
    return web.Response(text="OK", status=200)


async def ping_self_loop():
    url = os.environ.get("KOYEB_URL", "").strip()

    if not url:
        print("KOYEB_URL 환경변수가 존재하지 않습니다.")
        return

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as res:
                    print(f"✅ Self-ping 성공: {res.status} (URL: {url})")
        except Exception as e:
            print(f"❌ Self-ping 실패: {type(e).__name__}: {e} (URL: {url})")

        await asyncio.sleep(300)  # 5분 간격

async def main():
    # HTTP 서버 설정
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    
    # Slack 핸들러 설정
    handler = AsyncSocketModeHandler(
        app=slack_app,
        app_token=settings.SLACK_APP_TOKEN,
    )
    
    try:
        # HTTP 서버 시작
        await site.start()
        print("Health check server started on port 8000")
        
        # Self-ping 태스크 시작
        ping_task = asyncio.create_task(ping_self_loop())
        print("Self-ping task started")
        
        # Slack 연결 시작
        await handler.start_async()
        print("Slack Socket Mode started")
        
    finally:
        if 'ping_task' in locals():
            ping_task.cancel()
        await handler.close_async()
        await runner.cleanup()
        print("서버가 종료되었습니다.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")