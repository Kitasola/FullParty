# discord.pyライブラリをインポート
import discord
# データベース操作用のモジュールをインポート
from database import cursor, conn

async def cleanup_old_events(client):
    for guild in client.guilds:
        try:
            # ギルド内のスケジュールされたイベントを取得
            events = await guild.fetch_scheduled_events()
            for event in events:
                # イベントが1日以上経過している場合
                if (discord.utils.utcnow() - event.start_time).total_seconds() > 86400:
                    # イベントを削除
                    await event.delete()
                    print(f"削除されたイベント: {event.name}")

                    # イベント削除時にDBのレコードも削除
                    cursor.execute("DELETE FROM event_info WHERE event_id = ?", (event.id,))
                    conn.commit()
                    print(f"削除されたDBレコード: イベントID {event.id}")
        except Exception as e:
            print(f"Error while cleaning up events in guild {guild.name}: {e}")