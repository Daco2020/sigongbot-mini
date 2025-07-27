from supabase.client import AsyncClient

from config import settings


class SupabaseClient:
    _instance = None

    @classmethod
    def get_instance(cls) -> AsyncClient:
        """싱글톤 패턴으로 Supabase 클라이언트 인스턴스를 반환합니다."""
        if cls._instance is None:
            cls._instance = AsyncClient(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY,
            )
        return cls._instance


supabase = SupabaseClient.get_instance()
