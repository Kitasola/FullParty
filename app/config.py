# osモジュールをインポート
import os
# dotenvライブラリをインポートし、環境変数を読み込む
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 環境変数の設定
# Discord Botのトークン
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# 開発用ギルドID
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")
# 環境タイプ (デフォルトは本番環境)
ENV_TYPE = os.getenv("ENV_TYPE", "production")
# マップ画像の保存先ディレクトリ (絶対パス)
MAP_IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../image/maps/"))
MAP_INFO_CSV =  os.path.join(MAP_IMAGE_DIR, "map_info.csv")
# データベースファイルのパス
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../server_settings.db"))