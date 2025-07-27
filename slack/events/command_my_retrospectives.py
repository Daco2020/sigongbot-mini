from slack.types import CommandBodyType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.views import View
from slack_sdk.models.blocks import SectionBlock, DividerBlock, ButtonElement, Block
from loguru import logger

from database.retrospective import get_retrospectives_by_user_id


async def handle_command_my_retrospectives(
    ack: AsyncAck, body: CommandBodyType, client: AsyncWebClient
):
    """내 회고 목록 명령어 처리"""
    await ack()

    user_id = body["user_id"]

    try:
        # 사용자의 회고 데이터 가져오기
        retrospectives = await get_retrospectives_by_user_id(user_id)

        if not retrospectives:
            # 회고가 없는 경우
            blocks: list[Block] = [
                SectionBlock(
                    text="아직 작성한 회고가 없습니다. `/공유` 명령어를 사용하여 회고를 공유해보세요!"
                )
            ]
        else:
            # 헤더 블록
            blocks = [
                SectionBlock(text="*내가 작성한 회고 목록*"),
                DividerBlock(),
            ]

            # created_at 시간 초 까지 표시
            # 회고 목록 블록 생성
            for retro in retrospectives:
                retro_id = retro["id"]
                session_name = retro["session_name"]
                created_at = (
                    retro["created_at"].split("T")[0]
                    + " "
                    + retro["created_at"].split("T")[1].split(".")[0]
                )

                # 회고 항목 블록
                blocks.append(
                    SectionBlock(
                        text=f"*{session_name}* ({created_at})",
                        accessory=ButtonElement(
                            text="상세보기",
                            value=f"{retro_id}",
                            action_id="view_retrospective_detail",
                        ),
                    )
                )

                # 구분선 추가 (마지막 항목에는 추가하지 않음)
                if retro != retrospectives[-1]:
                    blocks.append(DividerBlock())

        # 모달 뷰 생성
        view = View(
            type="modal",
            title="내 회고 목록",
            close="닫기",
            blocks=blocks,
        )

        # 모달 열기
        await client.views_open(trigger_id=body["trigger_id"], view=view)

    except Exception as e:
        logger.error(f"회고 목록 조회 실패 - User: {user_id}, Error: {str(e)}")
        # 오류 메시지 모달
        blocks = [
            SectionBlock(text=f"회고 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")
        ]

        view = View(
            type="modal",
            title="오류",
            close="확인",
            blocks=blocks,
        )

        await client.views_open(trigger_id=body["trigger_id"], view=view)
