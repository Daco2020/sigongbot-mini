import os
from dotenv import load_dotenv

if os.getenv("ENV", "dev") == "dev":
    load_dotenv()

class Settings:
    def __init__(self):
        self.ENV: str = os.getenv("ENV", "dev")

        self.SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
        self.SLACK_APP_TOKEN: str = os.getenv("SLACK_APP_TOKEN", "")

        self.ADMIN_CHANNEL: str = os.getenv("ADMIN_CHANNEL", "")
        self.SUPPORT_CHANNEL: str = os.getenv("SUPPORT_CHANNEL", "")

        self.ADMIN_IDS: list[str] = os.getenv("ADMIN_IDS", [])

        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

settings = Settings()
