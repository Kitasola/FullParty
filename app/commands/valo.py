from discord import app_commands
import discord
from database import cursor
import random
import os
from config import MAP_IMAGE_DIR

# VALORANT関連のコマンドグループを作成
valo_group = app_commands.Group(name="valo", description="VALORANT関連のコマンド")

# マップ抽選コマンド
@valo_group.command(name="map", description="マップの抽選を行います")
async def random_map(interaction: discord.Interaction):
    # データベースからマップ情報を取得
    cursor.execute("SELECT map_name_en, map_name_jp, map_image_path FROM map_info")
    maps = cursor.fetchall()

    if not maps:
        await interaction.response.send_message("マップ情報が登録されていません。", ephemeral=True)
        return

    # ランダムにマップを選択
    selected_map = random.choice(maps)
    map_name_en, map_name_jp, map_image_path = selected_map

    # マップ画像の保存先ディレクトリを使用してパスを構築
    map_image_path = os.path.join(MAP_IMAGE_DIR, map_image_path)

    # メッセージを送信
    embed = discord.Embed(title="抽選結果", description=f"選ばれたマップ: {map_name_jp} ({map_name_en})")
    if map_image_path:
        file = discord.File(map_image_path, filename="map.png")
        embed.set_image(url=f"attachment://map.png")
        await interaction.response.send_message(embed=embed, file=file)
    else:
        await interaction.response.send_message(embed=embed)

__all__ = ["valo_group"]