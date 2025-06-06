import discord
from database import cursor
import random
import os
from config import MAP_IMAGE_DIR
from discord.ui import View, Button

class MapResponseView(View):
    def __init__(self, interaction: discord.Interaction, rank: int, rank_name: str):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.message = None
        self.rank = rank
        self.rank_name = rank_name

    async def update_message(self):
        # データベースからマップ情報を取得
        sql = "SELECT map_name_en, map_name_jp, map_image_path FROM map_info"
        # rankの値に応じてSQLクエリを変更
        # ALL(-1): 全てのマップ, RANK(1): ランクマップのみ, NOT_RANK(0): ランクマップ以外
        if self.rank == -1:
            cursor.execute(sql)
        else:
            sql += " WHERE is_rank = ?"
            cursor.execute(sql, (self.rank,))
        maps = cursor.fetchall()

        if not maps:
            await self.interaction.response.send_message("マップ情報が登録されていません。", ephemeral=True)
            return

        # ランダムにマップを選択
        selected_map = random.choice(maps)
        map_name_en, map_name_jp, map_image_path = selected_map

        # マップ画像の保存先ディレクトリを使用してパスを構築
        map_image_path = os.path.join(MAP_IMAGE_DIR, map_image_path)
        # メッセージを送信
        embed = discord.Embed(title=f"抽選結果({self.rank_name})", description=f"**{map_name_jp}** ({map_name_en})", color=0x3498db)
        if map_image_path:
            file = discord.File(map_image_path, filename="map.png")
            embed.set_image(url=f"attachment://map.png")
            if self.message:
                await self.message.delete()
            self.message = await self.interaction.channel.send(embed=embed, file=file, view=self)
        else:
            if self.message:
                await self.message.delete() 
            self.message = await self.interaction.channel.send(embed=embed, view=self)

    @discord.ui.button(label="REROLL", style=discord.ButtonStyle.primary)
    async def reroll_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()  # 応答を遅延させる
        await self.update_message()

__all__ = ["MapResponseView"]