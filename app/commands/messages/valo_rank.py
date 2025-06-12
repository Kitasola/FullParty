# discord.pyのapp_commandsをインポート
import discord
from discord.ui import View
from database import cursor
from utils import VALO_RANK, VALO_DIV

class RankDivSelectView(View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.rank = None
        self.div = None

    async def send_message(self):
        cursor.execute("SELECT rank, div FROM user_info WHERE guild_id = ? AND user_id = ?", (self.interaction.guild.id, self.interaction.user.id))
        result = cursor.fetchone()
        if result is None:
            message = "現在のランク: 未登録"
        else:
            message = f"現在のランク: {result[0]} {result[1]}"
        await self.interaction.response.send_message(content=message, view=self)

    @discord.ui.select(
        placeholder="Rankを選択してください",
        options=[discord.SelectOption(label=f"{rank}") for rank in VALO_RANK.keys()],
        custom_id="rank_select"
    )
    async def rank_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.rank = select.values[0]
        if self.rank == "Radiant":
            self.div = "1"
            await interaction.response.send_message(f"{self.rank} を選択しました。divの選択は必要ありません。", ephemeral=True)
        else:
            await interaction.response.defer()

    @discord.ui.select(
        placeholder="Divを選択してください",
        options=[discord.SelectOption(label=f"{div}") for div in VALO_DIV.keys()],
        custom_id="div_select"
    )
    async def div_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.div = select.values[0]
        if self.rank == "Radiant":
            self.div = "1"
            await interaction.response.send_message(f"{self.rank} を選択しました。", ephemeral=True)
        else:
            await interaction.response.send_message(f"{self.rank} {self.div} を選択しました。", ephemeral=True)
