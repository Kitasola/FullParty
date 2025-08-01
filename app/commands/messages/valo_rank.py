# discord.pyのapp_commandsをインポート
import discord
from discord.ui import View
from database import cursor
from utils import VALO_RANK, VALO_DIV
from typing import Callable, Optional, Awaitable

class RankDivSelectView(View):
    def __init__(self, 
                 interaction: discord.Interaction,
                 callback: Optional[Callable[..., Awaitable[None]]] = None):
        super().__init__()
        self.interaction = interaction
        self.rank = None
        self.div = None
        self.callback = callback

    async def send_message(self):
        cursor.execute("SELECT rank, div FROM user_info WHERE guild_id = ? AND user_id = ?", (self.interaction.guild.id, self.interaction.user.id))
        result = cursor.fetchone()
        if result is None:
            message = "現在のランク: 未登録"
        else:
            message = f"現在のランク: {result[0]} {result[1]}"
        await self.interaction.followup.send(content=message, view=self, ephemeral=True)
        return result is not None

    @discord.ui.select(
        placeholder="Rankを選択してください",
        options=[discord.SelectOption(label=f"{rank}") for rank in VALO_RANK.keys()],
        custom_id="rank_select"
    )
    async def rank_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer()
        self.rank = select.values[0]
        if self.rank == "Radiant":
            self.div = "1"

    @discord.ui.select(
        placeholder="Divを選択してください",
        options=[discord.SelectOption(label=f"{div}") for div in VALO_DIV.keys()],
        custom_id="div_select"
    )
    async def div_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer()
        self.div = select.values[0]

    @discord.ui.button(label="REG", style=discord.ButtonStyle.primary, custom_id="register_button")
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ユーザーがRankとDivを選択しているか確認
        if self.rank is None or self.div is None:
            await interaction.response.send_message("RankとDivを選択してください。", ephemeral=True)
            return

        # RankがRadiantの場合、Divは1に固定
        if self.rank == "Radiant":
            self.div = "1"

        # データベースに登録
        cursor.execute(
            "INSERT OR REPLACE INTO user_info (guild_id, user_id, rank, div) VALUES (?, ?, ?, ?)",
            (self.interaction.guild.id, self.interaction.user.id, self.rank, self.div)
        )
        cursor.connection.commit()

        if self.callback:
            await self.callback()
        await interaction.response.send_message(f"{self.rank} {self.div} で登録しました。", ephemeral=True)