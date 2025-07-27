import asyncio
import signal
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from config import settings
from slack.event_handler import app as slack_app

async def main():  
    handler = AsyncSocketModeHandler(
        app=slack_app,
        app_token=settings.SLACK_APP_TOKEN,
    )
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())