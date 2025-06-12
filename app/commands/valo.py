from discord import app_commands
import discord
from .messages.map import MapResponseView
from .logic.valo_team import create as valo_team_create

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

class RankDivSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.rank = None
        self.div = None

    @discord.ui.select(
        placeholder="ランクを選択してください",
        options=[
            discord.SelectOption(label="Iron"),
            discord.SelectOption(label="Bronze"),
            discord.SelectOption(label="Silver"),
            discord.SelectOption(label="Gold"),
            discord.SelectOption(label="Platinum"),
            discord.SelectOption(label="Diamond"),
            discord.SelectOption(label="Ascendant"),
            discord.SelectOption(label="Immortal"),
            discord.SelectOption(label="Radiant"),
        ],
        custom_id="rank_select"
    )
    async def rank_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.rank = select.values[0]

    @discord.ui.select(
        placeholder="Divを選択してください",
        options=[
            discord.SelectOption(label="1"),
            discord.SelectOption(label="2"),
            discord.SelectOption(label="3"),
        ],
        custom_id="div_select"
    )
    async def div_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.div = select.values[0]
        await interaction.response.send_message(f"{self.rank} {self.div} を選択しました。", ephemeral=True)

# ランク入力コマンド
@valo_group.command(name="rank", description="ランクを申請します")
async def apply_rank(interaction: discord.Interaction):
    view = RankDivSelectView()
    await interaction.response.send_message("ランクとDivを選択してください。", view=view)


# チーム分けコマンド
@valo_group.command(name="team", description="チーム分けを行います")
async def create_team(interaction: discord.Interaction):
    # ユーザーのIDを取得
    from database import cursor, conn
    cursor.execute("SELECT user_id FROM user_info WHERE guild_id = ?", (interaction.guild.id,))
    users = [row[0] for row in cursor.fetchall()]
    if len(users) < 10:
        await interaction.response.send_message("チーム分けには最低10人のユーザーが必要です。", ephemeral=True)
        return
    try:
        team = await valo_team_create(interaction.guild.id, users, 2)
        team1 = ", ".join(str(user_id) for user_id in team["team1"])
        team2 = ", ".join(str(user_id) for user_id in team["team2"])
        await interaction.response.send_message(f"チーム1: {team1}\nチーム2: {team2}")
    except Exception as e:
        await interaction.response.send_message(f"チーム分けに失敗しました: {str(e)}", ephemeral=True)

__all__ = ["valo_group"]