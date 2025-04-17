# discord.pyのapp_commandsをインポート
from discord import app_commands
import discord
# データベース操作用のモジュールをインポート
from database import cursor, conn
from datetime import datetime, timezone, timedelta
from discord.ui import View, Button
from discord import Embed
from .messages.event import EventResponseView

# コマンドグループを作成
fp_group = app_commands.Group(name="fp", description="ゲーム募集関連のコマンド")

# デフォルトチャンネルを設定するコマンド
@fp_group.command(name="init", description="イベント作成のデフォルトチャンネルを設定します。")
@app_commands.describe(channel="デフォルトに設定するボイスチャンネルです。")
async def set_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
    guild_id = interaction.guild.id
    channel_id = channel.id

    # データベースにデフォルトチャンネルを保存
    cursor.execute("REPLACE INTO server_settings (guild_id, channel_id) VALUES (?, ?)", (guild_id, channel_id))
    conn.commit()

    # ユーザーに設定完了を通知
    await interaction.response.send_message(f"デフォルトチャンネルを {channel.mention} に設定しました。", ephemeral=True)

# ゲーム募集イベントを作成するコマンド
@fp_group.command(name="create", description="ゲーム募集イベントを作成します。")
@app_commands.describe(number_of_players="募集人数 (デフォルト: 5)", start_time="開始時間 (hh:mm形式、デフォルト: 21:00)", game_name="募集するゲーム名 (デフォルト: VALORANT)")
async def create_event(interaction: discord.Interaction, number_of_players: int = 5, start_time: str = "21:00", game_name: str = "VALORANT"):
    # 開始時間を検証
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        # Asia/Tokyoのタイムゾーンを適用
        tokyo_tz = timezone(timedelta(hours=9))
        now_tokyo = datetime.now(tokyo_tz)
        start_time_utc = now_tokyo.replace(hour=start_time_obj.hour, minute=start_time_obj.minute, second=0, microsecond=0).astimezone(timezone.utc)

        # 入力された時間が過去の場合
        if start_time_utc < now_tokyo.astimezone(timezone.utc):
            await interaction.response.send_message("開始時間が過去の時間です。未来の時間を指定してください。", ephemeral=True)
            return

        # デフォルトの21:00が指定され、現在時刻が21:00以降の場合
        if start_time == "21:00" and now_tokyo.hour >= 21:
            start_time_utc = (now_tokyo + timedelta(minutes=30)).replace(second=0, microsecond=0).astimezone(timezone.utc)
    except ValueError:
        await interaction.response.send_message("開始時間の形式が正しくありません。hh:mm形式で入力してください (例: 21:00)。", ephemeral=True)
        return

    guild_id = interaction.guild.id
    cursor.execute("SELECT channel_id FROM server_settings WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()

    if not result:
        await interaction.response.send_message("デフォルトチャンネルが設定されていません。/fp init コマンドを使用して設定してください。", ephemeral=True)
        return

    channel_id = result[0]
    channel = interaction.guild.get_channel(channel_id)

    if not channel:
        await interaction.response.send_message("デフォルトチャンネルが無効です。/fp init コマンドを使用して再設定してください。", ephemeral=True)
        return

   # コマンドのレスポンスを送信
    await interaction.response.send_message("イベントの作成を受付ました。", ephemeral=True)

    # イベントを作成
    view = EventResponseView(
        interaction=interaction,
        game_name=game_name,
        number_of_players=number_of_players,
        start_time_utc=start_time_utc,
        channel=channel,
    )
    await view.update_message()

    # コマンド実行ユーザーを初期参加者として追加
    view.yes_users.add(interaction.user.id)
    await view.update_message()

    # イベント情報をデータベースに保存
    cursor.execute("INSERT INTO event_info (event_id, message_id, max_participants, recruitment_time, game_name) VALUES (?, ?, ?, ?, ?)",
                   (view.event.id, view.message.id, number_of_players, start_time_utc, game_name))
    conn.commit()