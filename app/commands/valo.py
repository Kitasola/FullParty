from discord import app_commands
import discord
from .messages.map import MapResponseView

# VALORANT関連のコマンドグループを作成
valo_group = app_commands.Group(name="valo", description="VALORANT関連のコマンド")

# マップ抽選コマンド
@valo_group.command(name="map", description="マップの抽選を行います")
async def random_map(interaction: discord.Interaction):
    await interaction.response.send_message("マップの抽選を受け付けました。", ephemeral=True)
    view = MapResponseView(interaction)
    await view.update_message()

__all__ = ["valo_group"]