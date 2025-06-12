from discord import app_commands
import discord
from .messages.map import MapResponseView
from .messages.valo_rank import RankDivSelectView
from .messages.valo_team import TeamResponseView

# VALORANT関連のコマンドグループを作成
valo_group = app_commands.Group(name="valo", description="VALORANT関連のコマンド")

# マップ抽選コマンド
@app_commands.describe(rank="対象マップ: ALL(デフォルト), RANK, NOT_RANK")
@app_commands.choices(rank=[
    app_commands.Choice(name="ALL", value="-1"),
    app_commands.Choice(name="RANK", value="1"),
    app_commands.Choice(name="NOT_RANK", value="0")
])
@valo_group.command(name="map", description="マップの抽選を行います")
async def random_map(
    interaction: discord.Interaction,
    rank: str = "-1"
):
    await interaction.response.send_message(f"マップの抽選を受け付けました。", ephemeral=True)
    match rank:
        case "-1":
            rank_name = "ALL"
        case "1":
            rank_name = "RANK"
        case "0":
            rank_name = "NOT_RANK"
        case _:
            rank_name = "ALL"
    view = MapResponseView(interaction, int(rank), rank_name)
    await view.update_message()

# ランク入力コマンド
@valo_group.command(name="rank", description="ランクを登録します")
async def apply_rank(interaction: discord.Interaction):
    view = RankDivSelectView(interaction)
    await view.send_message()

# チーム分けコマンド
@valo_group.command(name="team", description="チーム分けを行います")
async def create_team(interaction: discord.Interaction):
    view = TeamResponseView(interaction)
    await view.update_message()
    await interaction.response.send_message("チーム分けを開始しました。", ephemeral=True)

__all__ = ["valo_group"]