from slack_bolt.async_app import AsyncAck


async def handle_reaction_added(ack: AsyncAck, body: dict) -> None:
    await ack()
