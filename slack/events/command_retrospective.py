from slack.types import CommandBodyType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    InputBlock,
    PlainTextInputElement,
    NumberInputElement,
    SectionBlock,
)

from utils import (
    format_remaining_time,
    get_current_session_info,
    get_latest_temp_retrospective,
)
from database import check_user_submitted_this_session


async def handle_command_retrospective(
    ack: AsyncAck, body: CommandBodyType, client: AsyncWebClient
):
    """회고 제출 명령어 처리"""
    await ack()

    user_id = body["user_id"]

    # 현재 회차 정보 가져오기
    current_session_info = get_current_session_info()
    session_name = current_session_info[1]
    remaining_time = current_session_info[2]
    remaining_time_str = format_remaining_time(remaining_time)

    # 임시 저장된 데이터 확인
    temp_values = get_latest_temp_retrospective(user_id)

    # 사용자가 현재 회차에 이미 회고를 제출했는지 확인
    already_submitted = await check_user_submitted_this_session(
        user_id=user_id,
        session_name=session_name,
    )

    # 이미 제출한 경우 알림창 표시
    if already_submitted:
        view = View(
            type="modal",
            title="회고 공유",
            close="확인",
            blocks=[
                SectionBlock(
                    text=f"<@{user_id}>님은 이미 `{session_name}` 회고를 공유했어요! 🤗",
                ),
            ],
        )
        await client.views_open(trigger_id=body["trigger_id"], view=view)
        return

    # 블록 생성
    blocks = [
        SectionBlock(
            text=f"이번 회고 공유 회차는 `{session_name}` 입니다.\n공유 마감까지 남은 시간은 `{remaining_time_str}`입니다.",
        ),
        InputBlock(
            block_id="good_points",
            label="잘했고 좋았던 점을 알려주세요",
            element=PlainTextInputElement(
                action_id="good_points_input",
                multiline=True,
                min_length=1,
                max_length=500,
                initial_value=(
                    temp_values.get("good_points", "") if temp_values else None
                ),
            ),
        ),
        InputBlock(
            block_id="improvements",
            label="아쉽고 개선하고 싶은 점을 알려주세요",
            element=PlainTextInputElement(
                action_id="improvements_input",
                multiline=True,
                min_length=1,
                max_length=500,
                initial_value=(
                    temp_values.get("improvements", "") if temp_values else None
                ),
            ),
        ),
        InputBlock(
            block_id="learnings",
            label="새롭게 배운 점을 알려주세요",
            element=PlainTextInputElement(
                action_id="learnings_input",
                multiline=True,
                min_length=1,
                max_length=500,
                initial_value=temp_values.get("learnings", "") if temp_values else None,
            ),
        ),
        InputBlock(
            block_id="action_item",
            label="해볼만한 액션 아이템을 알려주세요",
            element=PlainTextInputElement(
                action_id="action_item_input",
                multiline=True,
                min_length=1,
                max_length=500,
                initial_value=(
                    temp_values.get("action_item", "") if temp_values else None
                ),
            ),
        ),
        InputBlock(
            optional=True,
            block_id="emotion_score",
            label="오늘의 감정점수를 알려주세요 (1-10)",
            element=NumberInputElement(
                action_id="emotion_score_input",
                is_decimal_allowed=False,
                min_value="1",
                max_value="10",
                initial_value=(
                    temp_values.get("emotion_score", "") if temp_values else None
                ),
            ),
        ),
        InputBlock(
            optional=True,
            block_id="emotion_reason",
            label="감정점수 이유를 알려주세요",
            element=PlainTextInputElement(
                action_id="emotion_reason_input",
                multiline=True,
                min_length=1,
                max_length=500,
                initial_value=(
                    temp_values.get("emotion_reason", "") if temp_values else None
                ),
            ),
        ),
    ]

    # 임시 저장 데이터가 있었다면 알림 추가
    if temp_values:
        blocks.insert(
            1, SectionBlock(text="🤗 이전에 저장하지 못한 임시 데이터를 불러왔어요!")
        )

    # 명령어가 실행된 채널 ID 저장
    channel_id = body["channel_id"]

    # 모달 뷰 생성
    view = View(
        type="modal",
        callback_id="retrospective_submit",
        title="회고 공유",
        submit="공유하기",
        blocks=blocks,
        private_metadata=channel_id,  # 채널 ID를 private_metadata에 저장
    )

    # 모달 열기
    await client.views_open(trigger_id=body["trigger_id"], view=view)
