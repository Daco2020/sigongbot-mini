from slack.types import CommandBodyType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    SectionBlock,
    DividerBlock,
    InputBlock,
    PlainTextInputElement,
    ActionsBlock,
    ButtonElement,
)

from config import settings
from database.retrospective import get_latest_retrospectives


async def handle_command_admin(
    ack: AsyncAck, body: CommandBodyType, client: AsyncWebClient
):
    """관리자 메뉴 명령어 처리"""
    await ack()

    user_id = body["user_id"]

    # 관리자 권한 확인
    if user_id not in settings.ADMIN_IDS:
        view = View(
            type="modal",
            title="접근 거부",
            close="확인",
            blocks=[
                SectionBlock(
                    text="관리자 기능에 접근할 권한이 없습니다. 관리자에게 문의하세요."
                ),
            ],
        )
        await client.views_open(trigger_id=body["trigger_id"], view=view)
        return

    # 최근 회고 데이터 가져오기 (최대 20개)
    retrospectives = await get_latest_retrospectives(limit=20)

    # 회고 목록 옵션 생성
    options_text = ""
    for retro in retrospectives:
        retro_id = retro["id"]
        retro_user = retro["user_id"]
        retro_session = retro["session_name"]
        created_at = (
            retro["created_at"].split("T")[0]
            + " "
            + retro["created_at"].split("T")[1].split(".")[0]
        )

        options_text += f"```회고ID: {retro_id} | {retro_session} | <@{retro_user}> | {created_at}\n```"

    # 관리자 메뉴 모달 생성
    blocks = [
        SectionBlock(
            text="관리자 메뉴에 오신 것을 환영합니다. 수행할 작업을 선택하세요."
        ),
        DividerBlock(),
        SectionBlock(text="*특정 멤버를 채널에 초대합니다*"),
        ActionsBlock(
            elements=[
                ButtonElement(
                    text="채널 초대",
                    action_id="invite_channel",
                    value="invite_channel",
                ),
            ],
        ),
        DividerBlock(),
        SectionBlock(text="*회고를 수정 또는 삭제합니다*"),
        InputBlock(
            block_id="retrospective_id",
            label="관리할 회고 ID",
            element=PlainTextInputElement(
                action_id="retrospective_id_input",
                placeholder="최근 회고 목록에서 ID를 확인하고 입력하세요",
            ),
        ),
        SectionBlock(text=f"*최근 회고 목록*\n\n{options_text}"),
    ]

    # 모달 뷰 생성
    view = View(
        type="modal",
        callback_id="admin_menu",
        title="관리자 메뉴",
        submit="다음",
        blocks=blocks,
        private_metadata=body["channel_id"],  # 채널 ID를 private_metadata에 저장
    )

    # 모달 열기
    await client.views_open(trigger_id=body["trigger_id"], view=view)
