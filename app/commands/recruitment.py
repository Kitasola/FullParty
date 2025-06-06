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
@app_commands.describe(number_of_players="募集人数 (デフォルト: 5)", start_time="開始時間 (hh:mm形式、デフォルト: 平日: 21:00, 土日: 13:00)", game_name="募集するゲーム名 (デフォルト: VALORANT)", voice_channel="募集を行うボイスチャンネル (デフォルト: 設定済みのデフォルトチャンネル)")
async def create_event(interaction: discord.Interaction, number_of_players: int = 5, start_time: str = None, game_name: str = "VALORANT", voice_channel: discord.VoiceChannel = None):
    # 基準(今日)となるdatetimeオブジェクトを取得
    tokyo_tz = timezone(timedelta(hours=9))
    today = datetime.now(tokyo_tz)

    # 曜日によるデフォルト値の設定
    if start_time is None:
        if today.weekday() >= 5 and today.hour < 13:  # 土日13:00以前
            default_start_datetime = today.replace(hour=13, minute=0, second=0, microsecond=0)
        else:  # 平日
            default_start_datetime = today.replace(hour=21, minute=0, second=0, microsecond=0)

    # 開始時間を検証
    try:
        if start_time is None:
            # デフォルトの時間が指定され、現在時刻が指定時間以降の場合は30分後に設定
            if today >= default_start_datetime:
                start_time_obj = (today + timedelta(minutes=30)).replace(second=0, microsecond=0)
            else:
                start_time_obj = default_start_datetime
        else:
            start_datetime_obj = datetime.strptime(start_time, "%H:%M")
            start_time_obj = today.replace(hour=start_datetime_obj.hour, minute=start_datetime_obj.minute)
    except ValueError:
        await interaction.response.send_message("開始時間の形式が正しくありません。hh:mm形式で入力してください (例: 21:00)。", ephemeral=True)
        return

    # 入力された時間が過去の場合
    if start_time_obj < today:
        await interaction.response.send_message("開始時間が過去の時間です。未来の時間を指定してください。", ephemeral=True)
        return

    # ボイスチャンネルのチェック
    if voice_channel is None:
        guild_id = interaction.guild.id
        cursor.execute("SELECT channel_id FROM server_settings WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()

        if not result:
            await interaction.response.send_message("デフォルトチャンネルが設定されていません。/fp init コマンドを使用して設定してください。", ephemeral=True)
            return

        channel_id = result[0]
        voice_channel = interaction.guild.get_channel(channel_id)

        if not voice_channel:
            await interaction.response.send_message("デフォルトチャンネルが無効です。/fp init コマンドを使用して再設定してください。", ephemeral=True)
            return

    # コマンドのレスポンスを送信
    await interaction.response.send_message("イベントの作成を受付ました。", ephemeral=True)

    # イベントを作成
    view = EventResponseView(
        interaction=interaction,
        game_name=game_name,
        number_of_players=number_of_players,
        start_time_utc=start_time_obj.astimezone(timezone.utc),
        channel=voice_channel,
    )
    await view.update_message()

    # コマンド実行ユーザーを初期参加者として追加
    view.yes_users.add(interaction.user.id)
    await view.update_message()

    # イベント情報をデータベースに保存
    cursor.execute("INSERT INTO event_info (event_id, message_id, max_participants, recruitment_time, game_name, available_count, unavailable_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (view.event.id, view.message.id, number_of_players, start_time_obj.astimezone(timezone.utc), game_name, len(view.yes_users), len(view.no_users)))
    conn.commit()