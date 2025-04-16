# recruitment.pyからコマンドグループをインポート
from .recruitment import fp_group
from .valo import valo_group

# コマンドを登録する関数
def register_commands(client):
    print("Registering commands...")
    # コマンドグループをクライアントに追加
    client.tree.add_command(fp_group)
    print(f"Registered command group: {fp_group.name}")
    # VALORANT関連コマンドを登録
    client.tree.add_command(valo_group)
    print(f"Registered command group: {valo_group.name}")

# モジュールとして公開する関数を定義
__all__ = ["register_commands"]