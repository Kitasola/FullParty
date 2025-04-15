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

# イベントとチャンネルのマッピングテーブル
cursor.execute("""
CREATE TABLE IF NOT EXISTS event_channels (
    event_id INTEGER PRIMARY KEY,
    channel_id INTEGER
)
""")
conn.commit()

# イベントとチャンネルのマッピングテーブルにメッセージ送信済みフラグを追加
try:
    cursor.execute("""
    ALTER TABLE event_channels ADD COLUMN message_sent BOOLEAN DEFAULT 0
    """)
    conn.commit()
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'message_sent' already exists. Skipping ALTER TABLE.")
    else:
        raise