from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from config import settings
from slack.types import ChannelCreatedBodyType


async def handle_channel_created(
    ack: AsyncAck,
    body: ChannelCreatedBodyType,
    client: AsyncWebClient,
):
    """공개 채널 생성 이벤트를 처리합니다."""
    await ack()

    channel_id = body["event"]["channel"]["id"]
    await client.conversations_join(channel=channel_id)
    await client.chat_postMessage(
        channel=settings.ADMIN_CHANNEL,
        text=f"새로 만들어진 <#{channel_id}> 채널에 시공봇이 참여했습니다. 😋",
    )
