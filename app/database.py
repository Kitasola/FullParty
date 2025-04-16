# sqlite3モジュールをインポート
import sqlite3

# SQLite データベースのセットアップ
# データベースファイルのパス
db_path = "server_settings.db"
# データベース接続を作成
conn = sqlite3.connect(db_path)
# カーソルを作成
cursor = conn.cursor()

# サーバー設定テーブルの作成
# ギルドID (プライマリキー) とチャンネルID を含む
cursor.execute("""
CREATE TABLE IF NOT EXISTS server_settings (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER
)
""")

# イベント情報テーブルの作成
# イベントID、チャンネルID、メッセージ送信フラグ、最大参加人数などを含む
cursor.execute("""
CREATE TABLE IF NOT EXISTS event_info (
    event_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    message_sent BOOLEAN DEFAULT 0,
    max_participants INTEGER,
    recruitment_time DATETIME,
    game_name TEXT,
    available_count INTEGER DEFAULT 0,
    unavailable_count INTEGER DEFAULT 0
)
""")

# マップ情報テーブルの作成
# マップID、マップ名（英語・日本語）、マップ画像のローカルパスを含む
cursor.execute("""
CREATE TABLE IF NOT EXISTS map_info (
    map_id INTEGER PRIMARY KEY AUTOINCREMENT,
    map_name_en TEXT NOT NULL,
    map_name_jp TEXT NOT NULL,
    map_image_path TEXT
)
""")

# テーブル作成の変更を保存
conn.commit()