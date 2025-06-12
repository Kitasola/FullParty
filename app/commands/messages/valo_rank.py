# discord.pyのapp_commandsをインポート
import discord
from discord.ui import View, Button
from discord import Embed
from utils import VALO_RANK, VALO_DIV

class RankDivSelectView(View):
    def __init__(self):
        super().__init__()
        self.rank = None
        self.div = None

    @discord.ui.select(
        placeholder="ランクを選択してください",
        options=[discord.SelectOption(label=f"{rank}") for rank in VALO_RANK.keys()],
        custom_id="rank_select"
    )
    async def rank_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.rank = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Divを選択してください",
        options=[discord.SelectOption(label=f"{div}") for div in VALO_DIV.keys()],
        custom_id="div_select"
    )
    async def div_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.div = select.values[0]
        await interaction.response.send_message(f"{self.rank} {self.div} を選択しました。", ephemeral=True)
