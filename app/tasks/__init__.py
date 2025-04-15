from .event_tasks import monitor_event_participants, cleanup_old_events

def register_tasks(client, scheduler):
    scheduler.add_job(lambda: monitor_event_participants(client), 'interval', minutes=1)  # 1分ごとに実行
    scheduler.add_job(lambda: cleanup_old_events(client, scheduler), 'cron', hour=5)  # 毎日午前5時に実行

__all__ = ["register_tasks"]