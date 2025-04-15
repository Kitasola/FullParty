from .event_tasks import monitor_event_participants, cleanup_old_events
import asyncio
from asyncio import get_event_loop

def register_tasks(client, scheduler):
    loop = get_event_loop()
    scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(monitor_event_participants(client), loop), 'interval', minutes=1)  # 1分ごとに実行
    scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(cleanup_old_events(client, scheduler), loop), 'cron', hour=5)  # 毎日午前5時に実行

__all__ = ["register_tasks"]