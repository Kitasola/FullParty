# discord.pyライブラリをインポート
import discord
# データベース操作用のモジュールをインポート
from database import cursor, conn

# 必要な情報を引数として受け取るように変更
async def monitor_event_participants(client):
    for guild in client.guilds:
        try:
            # ギルド内のスケジュールされたイベントを取得
            events = await guild.fetch_scheduled_events()
            for event in events:
                if event.status == discord.EventStatus.scheduled:
                    # イベントの参加者を取得
                    attendees = [user async for user in event.users()]
                    # 募集人数をevent.nameから抽出
                    required_attendees = int(event.name.split("@")[1])
                    if len(attendees) >= required_attendees:
                        cursor.execute("SELECT channel_id, message_sent FROM event_info WHERE event_id = ?", (event.id,))
                        result = cursor.fetchone()
                        if result:
                            channel_id, message_sent = result
                            if not message_sent:
                                # メッセージを送信
                                channel = guild.get_channel(channel_id)
                                if channel:
                                    await channel.send(f"〆 {event.name} {event.description}")
                                    cursor.execute("UPDATE event_info SET message_sent = 1 WHERE event_id = ?", (event.id,))
                                    conn.commit()
        except Exception as e:
            print(f"Error while monitoring events in guild {guild.name}: {e}")

async def cleanup_old_events(client, scheduler):
    # タスクを一時停止
    scheduler.pause_job('monitor_event_participants')
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
    # タスクを再開
    scheduler.resume_job('monitor_event_participants')