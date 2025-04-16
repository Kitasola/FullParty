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
cursor.execute("""
CREATE TABLE IF NOT EXISTS server_settings (
    guild_id INTEGER PRIMARY KEY,  # ギルドID (プライマリキー)
    channel_id INTEGER             # チャンネルID
)
""")

# イベント情報テーブルの作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS event_info (
    event_id INTEGER PRIMARY KEY,      # イベントID (プライマリキー)
    channel_id INTEGER,                # チャンネルID
    message_sent BOOLEAN DEFAULT 0,    # メッセージ送信フラグ (デフォルト: 0)
    max_participants INTEGER,          # 最大参加人数
    recruitment_time DATETIME,         # 募集時間
    game_name TEXT,                    # ゲーム名
    available_count INTEGER DEFAULT 0, # 参加可能人数 (デフォルト: 0)
    unavailable_count INTEGER DEFAULT 0 # 参加不可能人数 (デフォルト: 0)
)
""")
# テーブル作成の変更を保存
conn.commit()