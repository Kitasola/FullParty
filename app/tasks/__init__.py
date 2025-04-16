# recruitment.pyからタスク関数をインポート
from .recruitment import monitor_event_participants, cleanup_old_events
import asyncio
from asyncio import get_event_loop

# タスクを登録する関数
def register_tasks(client, scheduler):
    # 非同期イベントループを取得
    loop = get_event_loop()
    # 1分ごとに参加者を監視するタスクをスケジューラに追加
    scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(monitor_event_participants(client), loop), 'interval', minutes=1)
    # 毎日午前5時に古いイベントを削除するタスクをスケジューラに追加
    scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(cleanup_old_events(client, scheduler), loop), 'cron', hour=5)

# モジュールとして公開する関数を定義
__all__ = ["register_tasks"]