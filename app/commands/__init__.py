# recruitment.pyからコマンドグループをインポート
from .recruitment import fp_group

# コマンドを登録する関数
def register_commands(client):
    print("Registering commands...")
    # コマンドグループをクライアントに追加
    client.tree.add_command(fp_group)
    print(f"Registered command group: {fp_group.name}")

# モジュールとして公開する関数を定義
__all__ = ["register_commands"]