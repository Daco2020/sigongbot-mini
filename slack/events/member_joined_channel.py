from slack_bolt.async_app import AsyncAck


async def handle_member_joined_channel(ack: AsyncAck, body: dict) -> None:
    await ack()
