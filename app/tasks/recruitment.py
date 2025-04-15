import discord
from database import cursor, conn

# 必要な情報を引数として受け取るように変更
async def monitor_event_participants(client):
    for guild in client.guilds:
        try:
            events = await guild.fetch_scheduled_events()
            for event in events:
                if event.status == discord.EventStatus.scheduled:
                    attendees = [user async for user in event.users()]
                    required_attendees = int(event.name.split("@")[1])  # 募集人数をevent.nameから抽出
                    if len(attendees) >= required_attendees:
                        cursor.execute("SELECT channel_id, message_sent FROM event_channels WHERE event_id = ?", (event.id,))
                        result = cursor.fetchone()
                        if result:
                            channel_id, message_sent = result
                            if not message_sent:
                                channel = guild.get_channel(channel_id)
                                if channel:
                                    await channel.send(f"〆 {event.name} {event.description}")
                                    cursor.execute("UPDATE event_channels SET message_sent = 1 WHERE event_id = ?", (event.id,))
                                    conn.commit()
        except Exception as e:
            print(f"Error while monitoring events in guild {guild.name}: {e}")

async def cleanup_old_events(client, scheduler):
    scheduler.pause_job('monitor_event_participants')
    for guild in client.guilds:
        try:
            events = await guild.fetch_scheduled_events()
            for event in events:
                if (discord.utils.utcnow() - event.start_time).total_seconds() > 86400:  # 1日以上経過
                    await event.delete()
                    print(f"削除されたイベント: {event.name}")
        except Exception as e:
            print(f"Error while cleaning up events in guild {guild.name}: {e}")
    scheduler.resume_job('monitor_event_participants')