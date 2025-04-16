import sqlite3

# SQLite データベースのセットアップ
db_path = "server_settings.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# サーバー設定テーブル
cursor.execute("""
CREATE TABLE IF NOT EXISTS server_settings (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER
)
""")

# イベント情報テーブル
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
conn.commit()