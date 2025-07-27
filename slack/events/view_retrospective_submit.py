import asyncio
from loguru import logger
from slack.types import ViewBodyType, ViewType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.blocks import SectionBlock, DividerBlock, ContextBlock

from utils import get_current_session_info
from config import settings
from database.retrospective import create_retrospective
from utils import save_temp_retrospective, cleanup_temp_files


async def handle_view_retrospective_submit(
    ack: AsyncAck, body: ViewBodyType, client: AsyncWebClient, view: ViewType
):
    """모달 제출 처리"""
    user_id = body["user"]["id"]

    try:
        # 모달에서 입력된 값 추출
        values = view["state"]["values"]

        # 각 필드의 입력값 추출
        good_points = (
            values["good_points"]["good_points_input"]["value"] or "작성되지 않음"
        )
        improvements = (
            values["improvements"]["improvements_input"]["value"] or "작성되지 않음"
        )
        learnings = values["learnings"]["learnings_input"]["value"] or "작성되지 않음"
        action_item = (
            values["action_item"]["action_item_input"]["value"] or "작성되지 않음"
        )

        # 선택적 필드 처리
        emotion_score = (
            values.get("emotion_score", {})
            .get("emotion_score_input", {})
            .get("value", "")
        )
        emotion_reason = (
            values.get("emotion_reason", {})
            .get("emotion_reason_input", {})
            .get("value", "")
        )

        # 현재 회차 정보 가져오기
        current_session_info = get_current_session_info()
        session_name = current_session_info[1]

        # 메시지 블록 생성
        blocks = [
            SectionBlock(
                text=f"*<@{user_id}>님이 `{session_name}` 회고를 공유했어요! 🤗*"
            ),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*잘했고 좋았던 점* 🌟"}]
            ),
            SectionBlock(text=good_points),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*아쉽고 개선하고 싶은 점* 🔧"}]
            ),
            SectionBlock(text=improvements),
            DividerBlock(),
            ContextBlock(elements=[{"type": "mrkdwn", "text": "*새롭게 배운 점* 💡"}]),
            SectionBlock(text=learnings),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*해볼만한 액션 아이템* 🚀"}]
            ),
            SectionBlock(text=action_item),
        ]

        # 감정 점수가 입력되었다면 추가
        if emotion_score:
            blocks.extend(
                [
                    DividerBlock(),
                    SectionBlock(
                        text=f"*오늘의 감정점수* :bar_chart: {emotion_score}/10"
                    ),
                ]
            )

            # 감정 이유가 입력되었다면 추가
            if emotion_reason:
                blocks.append(SectionBlock(text=emotion_reason))

        # Footer 블록 생성
        footer_blocks = [
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

        blocks.extend(footer_blocks)

        # command_retrospective에서 호출된 채널 ID 가져오기
        original_channel_id = (
            body["view"]["private_metadata"]
            if body["view"].get("private_metadata")
            else body["user"]["id"]
        )

        await ack()

        # 원래의 채널에 회고 내용 게시
        response = await client.chat_postMessage(
            channel=original_channel_id,
            blocks=blocks,
            text=f"*<@{user_id}>님이 `{session_name}` 회고를 공유했어요! 🤗*",
        )

        # 메시지 타임스탬프 가져오기
        slack_ts = response["ts"]
        # Supabase에 데이터 저장
        await create_retrospective(
            user_id=user_id,
            session_name=session_name,
            slack_channel=original_channel_id,
            slack_ts=slack_ts,
            good_points=good_points,
            improvements=improvements,
            learnings=learnings,
            action_item=action_item,
            emotion_score=int(emotion_score) if emotion_score else None,
            emotion_reason=emotion_reason if emotion_reason else None,
        )

        # 성공적으로 저장되면 임시 파일 삭제
        cleanup_temp_files(user_id)

        # 로깅 추가
        logger.info(f"회고 제출 완료 - User: {user_id}")

    except Exception as e:
        logger.error(f"회고 제출 실패 - User: {user_id}, Error: {str(e)}")

        # 에러 발생 시 임시 저장
        try:
            save_temp_retrospective(
                user_id,
                {
                    "good_points": good_points,
                    "improvements": improvements,
                    "learnings": learnings,
                    "action_item": action_item,
                    "emotion_score": emotion_score,
                    "emotion_reason": emotion_reason,
                },
            )
        except Exception as save_error:
            logger.error(f"임시 저장 실패 - User: {user_id}, Error: {str(save_error)}")

        await ack(
            response_action="errors",
            errors={
                "good_points": "데이터 저장 중 오류가 발생했습니다. 다시 시도해주세요. (작성한 내용은 임시 저장되었습니다)"
            },
        )

    # 스레드에 추가 메시지 전송
    # 회고 공유와는 무관하므로 공유 완료 후 처리
    await asyncio.sleep(3)  # 부모 메시지 딜레이를 감안하여 3초 대기
    await client.chat_postMessage(
        channel=original_channel_id,
        thread_ts=slack_ts,  # 스레드로 연결
        text="멋진 회고를 공유해주셔서 고마워요! 타임트래커 이미지도 스레드에 공유해볼까요? 🖼️",
    )
