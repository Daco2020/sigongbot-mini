from slack.types import ViewBodyType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    SectionBlock,
    DividerBlock,
    ContextBlock,
)
from loguru import logger

from database.retrospective import get_retrospective_by_id
from config import settings


async def handle_action_view_retrospective_detail(
    ack: AsyncAck, body: ViewBodyType, client: AsyncWebClient, action: dict
):
    """회고 상세보기 액션 처리"""
    await ack()

    user_id = body["user"]["id"]
    retrospective_id = int(action["value"])

    try:
        # 회고 데이터 가져오기
        retrospective = await get_retrospective_by_id(retrospective_id)

        # 자신의 회고만 볼 수 있도록 체크
        if retrospective["user_id"] != user_id:
            # 권한 없음 메시지
            await client.views_open(
                trigger_id=body["trigger_id"],
                view=View(
                    type="modal",
                    title="접근 거부",
                    close="확인",
                    blocks=[
                        SectionBlock(text="다른 사용자의 회고는 볼 수 없습니다."),
                    ],
                ),
            )
            return

        # 회고 정보 추출
        session_name = retrospective["session_name"]
        created_at = (
            retrospective["created_at"].split("T")[0]
            if "T" in retrospective["created_at"]
            else retrospective["created_at"]
        )

        # 회고 상세 모달 블록 생성
        blocks = [
            SectionBlock(text=f"*{session_name}* ({created_at})"),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*잘했고 좋았던 점* 🌟"}]
            ),
            SectionBlock(text=retrospective["good_points"]),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*아쉽고 개선하고 싶은 점* 🔧"}]
            ),
            SectionBlock(text=retrospective["improvements"]),
            DividerBlock(),
            ContextBlock(elements=[{"type": "mrkdwn", "text": "*새롭게 배운 점* 💡"}]),
            SectionBlock(text=retrospective["learnings"]),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*해볼만한 액션 아이템* 🚀"}]
            ),
            SectionBlock(text=retrospective["action_item"]),
        ]

        # 감정 점수가 있는 경우 추가
        if retrospective.get("emotion_score"):
            blocks.extend(
                [
                    DividerBlock(),
                    SectionBlock(
                        text=f"*오늘의 감정점수* :bar_chart: {retrospective['emotion_score']}/10"
                    ),
                ]
            )

            # 감정 이유가 있는 경우 추가
            if retrospective.get("emotion_reason"):
                blocks.append(SectionBlock(text=retrospective["emotion_reason"]))

        # Footer 블록 추가
        blocks.extend(
            [
                DividerBlock(),
                ContextBlock(
                    elements=[
                        {
                            "type": "mrkdwn",
                            "text": f"회고에 문제가 있다면 <#{settings.SUPPORT_CHANNEL}>에 문의를 남겨 주세요.",
                        }
                    ]
                ),
            ]
        )

        # 상세 모달 표시 (views_push 사용)
        await client.views_push(
            trigger_id=body["trigger_id"],
            view=View(
                type="modal",
                title="회고 상세",
                close="뒤로가기",
                blocks=blocks,
            ),
        )

    except Exception as e:
        logger.error(
            f"회고 상세 조회 실패 - User: {user_id}, ID: {retrospective_id}, Error: {str(e)}"
        )
        # 오류 메시지 모달
        await client.views_open(
            trigger_id=body["trigger_id"],
            view=View(
                type="modal",
                title="오류",
                close="확인",
                blocks=[
                    SectionBlock(
                        text=f"회고 상세정보를 불러오는 중 오류가 발생했습니다: {str(e)}"
                    )
                ],
            ),
        )
