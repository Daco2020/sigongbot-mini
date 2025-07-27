from typing import Any

from loguru import logger

from database.supabase import supabase


async def create_retrospective(
    user_id: str,
    session_name: str,
    slack_channel: str,
    slack_ts: str,
    good_points: str,
    improvements: str,
    learnings: str,
    action_item: str,
    emotion_score: int | None = None,
    emotion_reason: str | None = None,
) -> dict[str, Any]:
    """
    회고 데이터를 Supabase에 저장합니다.

    Args:
        user_id: 사용자 ID
        session_name: 회차 정보
        slack_channel: 슬랙 채널 ID
        slack_ts: 슬랙 메시지 타임스탬프
        good_points: 잘한 점
        improvements: 개선할 점
        learnings: 배운 점
        action_item: 액션 아이템
        emotion_score: 감정 점수 (1-10)
        emotion_reason: 감정 점수 이유

    Returns:
        저장된 회고 데이터
    """
    try:
        data = {
            "user_id": user_id,
            "session_name": session_name,
            "slack_channel": slack_channel,
            "slack_ts": slack_ts,
            "good_points": good_points,
            "improvements": improvements,
            "learnings": learnings,
            "action_item": action_item,
            "emotion_score": emotion_score,
            "emotion_reason": emotion_reason,
        }

        # Supabase에 데이터 삽입
        result = await supabase.table("retrospectives").insert(data).execute()

        # 결과 확인 및 반환
        if len(result.data) > 0:
            logger.info(f"회고 저장 성공 - User: {user_id}")
            return result.data[0]
        else:
            logger.error(f"회고 저장 실패 - User: {user_id}, 결과 없음")
            raise ValueError("회고 저장에 실패했습니다.")

    except Exception as e:
        logger.error(f"회고 저장 실패 - User: {user_id}, Error: {str(e)}")
        raise ValueError(f"회고 저장 중 오류가 발생했습니다: {str(e)}")


async def get_retrospective_by_id(retrospective_id: int) -> dict[str, Any]:
    """
    ID로 회고 데이터를 조회합니다.

    Args:
        retrospective_id: 회고 ID

    Returns:
        회고 데이터
    """
    try:
        result = (
            await supabase.table("retrospectives")
            .select("*")
            .eq("id", retrospective_id)
            .execute()
        )

        if len(result.data) > 0:
            return result.data[0]
        else:
            raise ValueError(
                f"ID {retrospective_id}에 해당하는 회고를 찾을 수 없습니다."
            )

    except Exception as e:
        logger.error(f"회고 조회 실패 - ID: {retrospective_id}, Error: {str(e)}")
        raise ValueError(f"회고 조회 중 오류가 발생했습니다: {str(e)}")


async def get_retrospectives_by_user_id(user_id: str) -> list[dict[str, Any]]:
    """
    사용자 ID로 회고 데이터를 조회합니다.

    Args:
        user_id: 사용자 ID

    Returns:
        회고 데이터 목록
    """
    try:
        result = (
            await supabase.table("retrospectives")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return result.data

    except Exception as e:
        logger.error(f"사용자 회고 조회 실패 - User: {user_id}, Error: {str(e)}")
        raise ValueError(f"회고 조회 중 오류가 발생했습니다: {str(e)}")


async def check_user_submitted_this_session(user_id: str, session_name: str) -> bool:
    """
    사용자가 특정 회차에 회고를 제출했는지 확인합니다.

    Args:
        user_id: 사용자 ID
        session_name: 회차 이름

    Returns:
        제출 여부 (True/False)
    """
    try:
        query = (
            supabase.table("retrospectives")
            .select("id")
            .eq("user_id", user_id)
            .eq("session_name", session_name)
        )

        result = await query.execute()

        # 결과가 있으면 제출한 것으로 판단
        return len(result.data) > 0

    except Exception as e:
        logger.error(f"회고 제출 확인 실패 - User: {user_id}, Error: {str(e)}")
        # 오류 발생시 기본적으로 제출하지 않은 것으로 처리
        return False


async def update_retrospective(
    retrospective_id: int, data: dict[str, Any]
) -> dict[str, Any]:
    """
    회고 데이터를 업데이트합니다.

    Args:
        retrospective_id: 회고 ID
        data: 업데이트할 데이터

    Returns:
        업데이트된 회고 데이터
    """
    try:
        result = (
            await supabase.table("retrospectives")
            .update(data)
            .eq("id", retrospective_id)
            .execute()
        )

        if len(result.data) > 0:
            logger.info(f"회고 업데이트 성공 - ID: {retrospective_id}")
            return result.data[0]
        else:
            raise ValueError(
                f"ID {retrospective_id}에 해당하는 회고를 찾을 수 없습니다."
            )

    except Exception as e:
        logger.error(f"회고 업데이트 실패 - ID: {retrospective_id}, Error: {str(e)}")
        raise ValueError(f"회고 업데이트 중 오류가 발생했습니다: {str(e)}")


async def delete_retrospective(retrospective_id: int) -> bool:
    """
    회고 데이터를 삭제합니다.

    Args:
        retrospective_id: 회고 ID

    Returns:
        삭제 성공 여부
    """
    try:
        result = (
            await supabase.table("retrospectives")
            .delete()
            .eq("id", retrospective_id)
            .execute()
        )

        if len(result.data) > 0:
            logger.info(f"회고 삭제 성공 - ID: {retrospective_id}")
            return True
        else:
            logger.warning(f"삭제할 회고가 없음 - ID: {retrospective_id}")
            return False

    except Exception as e:
        logger.error(f"회고 삭제 실패 - ID: {retrospective_id}, Error: {str(e)}")
        raise ValueError(f"회고 삭제 중 오류가 발생했습니다: {str(e)}")


async def get_latest_retrospectives(limit: int = 10) -> list[dict[str, Any]]:
    """
    최근 회고 데이터를 조회합니다.

    Args:
        limit: 조회할 개수 (기본값: 10)

    Returns:
        최근 회고 데이터 목록
    """
    try:
        result = (
            await supabase.table("retrospectives")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data

    except Exception as e:
        logger.error(f"최근 회고 조회 실패 - Error: {str(e)}")
        raise ValueError(f"회고 조회 중 오류가 발생했습니다: {str(e)}")
