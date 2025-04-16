# botモジュールからクライアントをインポート
from bot import client
# configモジュールからトークンをインポート
from config import TOKEN

# Bot を実行
client.run(TOKEN)