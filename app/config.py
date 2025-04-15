import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 環境変数の設定
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")
ENV_TYPE = os.getenv("ENV_TYPE", "production")  # デフォルトは本番環境