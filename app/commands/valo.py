from discord import app_commands
import discord
from .messages.map import MapResponseView
from .logic.valo_team import create as valo_team_create
from .messages.valo_rank import RankDivSelectView

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
    # ユーザー情報の取得
    from database import cursor, conn
    cursor.execute("SELECT user_id, rank, div FROM user_info WHERE guild_id = ?", (interaction.guild.id,))
    result = cursor.fetchall()
    if not result:
        await interaction.response.send_message("チーム分けに必要なユーザー情報がありません。", ephemeral=True)
        return
    
    try:
        team = await valo_team_create(result)
        team1 = ", ".join(str(user_id) for user_id in team["team1"])
        team2 = ", ".join(str(user_id) for user_id in team["team2"])
        await interaction.response.send_message(f"チーム1: {team1}\nチーム2: {team2}")
    except ValueError as e:
        await interaction.response.send_message(f"チーム分けに失敗しました: {str(e)}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"予期しないエラーが発生しました", ephemeral=True)
        print(f"Error in create_team: {str(e)}")

__all__ = ["valo_group"]