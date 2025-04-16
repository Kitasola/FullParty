# recruitment.pyからタスク関数をインポート
from .recruitment import cleanup_old_events
import asyncio
from asyncio import get_event_loop

# タスクを登録する関数
def register_tasks(client, scheduler):
    # 非同期イベントループを取得
    loop = get_event_loop()
    # 毎日午前5時に古いイベントを削除するタスクをスケジューラに追加
    scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(cleanup_old_events(client), loop), 'cron', hour=5)

# モジュールとして公開する関数を定義
__all__ = ["register_tasks"]