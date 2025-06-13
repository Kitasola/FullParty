import discord
from database import cursor, conn
from discord.ui import View, Button
from logic import valo_team_create
from .valo_rank import RankDivSelectView
import asyncio

class TeamResponseView(View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.yes_users = set()
        self.no_users = set()
        self.message = None

    async def update_message(self):
        embed = discord.Embed(title="チーム分け", description="参加者リスト", color=0x3498db)
        embed.add_field(name=":thumbsup: YES", value="\n".join(f"<@{user_id}>" for user_id in self.yes_users) or "なし", inline=False)
        embed.add_field(name=":thumbsdown: NO", value="\n".join(f"<@{user_id}>" for user_id in self.no_users) or "なし", inline=False)
        embed.set_footer(text="ボタンをクリックして参加状況を更新してください。")
        
        if self.message is None:
            self.message = await self.interaction.channel.send(embed=embed, view=self)
        else:
            self.message = await self.message.edit(embed=embed, view=self)
        
    @discord.ui.button(label="YES", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("参加を受け付けました。\n次にランク情報の登録をしてください。\n※変更がない場合は入力不要です。", ephemeral=True)

        # ランク情報のチェック
        async def update_yes_users():
            if interaction.user.id in self.yes_users:
                self.yes_users.remove(interaction.user.id)
            self.yes_users.add(interaction.user.id)
            await self.update_message()

        view = RankDivSelectView(interaction, update_yes_users)
        is_rank_registered = await view.send_message()

        if is_rank_registered:
            await update_yes_users()

    @discord.ui.button(label="NO", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        if interaction.user.id in self.yes_users:
            self.yes_users.remove(interaction.user.id)
        self.no_users.add(interaction.user.id)
        await self.update_message()
    
    @discord.ui.button(label="RUN", style=discord.ButtonStyle.primary)
    async def create_team_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        # ユーザー情報の取得
        cursor.execute("SELECT user_id, rank, div FROM user_info WHERE guild_id = ?", (self.interaction.guild.id,))
        result = cursor.fetchall()
        if not result:
            await interaction.followup.send("チーム分けに必要なユーザー情報がありません。", ephemeral=True)
            return
        
        try:
            team = await valo_team_create(result)
            team1 = ", ".join(str(user_id) for user_id in team["team1"])
            team2 = ", ".join(str(user_id) for user_id in team["team2"])
            await interaction.followup.send(f"チーム1: {team1}\nチーム2: {team2}")
        except ValueError as e:
            await interaction.followup.send(f"チーム分けに失敗しました: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"予期しないエラーが発生しました: {str(e)}", ephemeral=True)