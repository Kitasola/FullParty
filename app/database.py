from config import MAP_INFO_CSV, DB_PATH
import sqlite3
import csv

# SQLite データベースのセットアップ
# データベース接続を作成
conn = sqlite3.connect(DB_PATH)
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
# イベントID、メッセージID、メッセージ送信フラグ、最大参加人数などを含む
cursor.execute("""
CREATE TABLE IF NOT EXISTS event_info (
    event_id INTEGER PRIMARY KEY,
    message_id INTEGER,
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

def initialize_map_info():
    with open(MAP_INFO_CSV, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # ヘッダーをスキップ
        cursor.execute("DELETE FROM map_info")  # 既存データを削除
        for row in reader:
            cursor.execute(
                "INSERT INTO map_info (map_id, map_name_en, map_name_jp, map_image_path) VALUES (?, ?, ?, ?)",
                (int(row[0]), row[1], row[2], row[3])
            )
        conn.commit()

# アプリケーション起動時にマップ情報を初期化
initialize_map_info()

# テーブル作成の変更を保存
conn.commit()