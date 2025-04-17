# discord.pyのapp_commandsをインポート
from discord import app_commands
import discord
# データベース操作用のモジュールをインポート
from database import cursor, conn
from datetime import datetime, timezone, timedelta
from discord.ui import View, Button
from discord import Embed

# 部分一致でフィールドを更新する関数
def update_field_by_partial_name(embed: discord.Embed, partial_name: str, num: int, value: str, inline: bool = False):
    for index, field in enumerate(embed.fields):
        if partial_name in field.name:  # 部分一致で検索
            embed.set_field_at(index, name=f"{partial_name} ({num}人)", value=value, inline=inline)
            return
    # フィールドが見つからない場合、新しいフィールドを追加
    embed.add_field(name=f"{partial_name} ({num}人)", value=value, inline=inline)

class EventResponseView(View):
    def __init__(self, message):
        super().__init__(timeout=None)
        self.yes_users = set()
        self.no_users = set()
        self.message = message

    async def update_message(self):
        embed = self.message.embeds[0]  # 既存の埋め込みメッセージを取得

        # 参加者リストを更新
        update_field_by_partial_name(embed, "参加可能者", len(self.yes_users), "\n".join(map(lambda user_id: f"<@{user_id}>", self.yes_users)) or "なし", inline=False)
        update_field_by_partial_name(embed, "参加不可者", len(self.no_users), "\n".join(map(lambda user_id: f"<@{user_id}>", self.no_users)) or "なし", inline=False)

        await self.message.edit(embed=embed, view=self)

    async def check_attendance(self, interaction: discord.Interaction):
        # 募集人数を取得
        cursor.execute("SELECT max_participants FROM event_info WHERE message_id = ?", (self.message.id,))
        result = cursor.fetchone()
        if not result:
            print("募集人数が見つかりませんでした。")
            return

        max_participants = result[0]
        yes_count = len(self.yes_users)

        # 募集人数に達しているか確認
        if yes_count >= max_participants:
            # message_sentを確認
            cursor.execute("SELECT message_sent FROM event_info WHERE message_id = ?", (self.message.id,))
            result = cursor.fetchone()
            if result and not result[0]:
                # message_sentをtrueに更新
                cursor.execute("UPDATE event_info SET message_sent = 1 WHERE message_id = ?", (self.message.id,))
                conn.commit()

                # 完了メッセージを返信
                await interaction.followup.send(f"〆", ephemeral=False)

                # イベントの説明を更新
                cursor.execute("SELECT event_id FROM event_info WHERE message_id = ?", (self.message.id,))
                result = cursor.fetchone()
                if result:
                    event_id = result[0]
                    event = await interaction.guild.fetch_scheduled_event(event_id)
                    await event.edit(description="募集完了")

    @discord.ui.button(label="YES", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()  # 応答を遅延させる
        if interaction.user.id in self.no_users:
            self.no_users.remove(interaction.user.id)
        self.yes_users.add(interaction.user.id)
        await self.update_message()
        await self.check_attendance(interaction)

    @discord.ui.button(label="NO", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()  # 応答を遅延させる
        if interaction.user.id in self.yes_users:
            self.yes_users.remove(interaction.user.id)
        self.no_users.add(interaction.user.id)
        await self.update_message()

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
@app_commands.describe(number_of_players="募集人数 (デフォルト: 4)", start_time="開始時間 (hh:mm形式、例: 21:00)", game_name="募集するゲーム名 (デフォルト: VALORANT)")
async def create_event(interaction: discord.Interaction, number_of_players: int = 4, start_time: str = "21:00", game_name: str = "VALORANT"):
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

    # イベントを作成
    event_name = f"{game_name}募集 @{number_of_players}"
    description = f"募集中"
    event = await interaction.guild.create_scheduled_event(
        name=event_name,
        description=description,
        start_time=start_time_utc,
        channel=channel,
        entity_type=discord.EntityType.voice,
        privacy_level=discord.PrivacyLevel.guild_only
    )

    # イベント作成メッセージを埋め込み形式で送信
    await interaction.response.send_message("イベントの作成を受付ました。", ephemeral=True)
    embed = Embed(title=f"{game_name}募集 @{number_of_players}", description=f"[イベントリンク]({event.url})", color=0x00ff00)
    embed.add_field(name="開始時間", value=start_time, inline=True)
    embed.add_field(name="ボイスチャンネル", value=channel.mention, inline=True)
    embed.add_field(name="参加者リスト", value="", inline=False)
    embed.set_footer(text="ボタンをクリックして参加状況を更新してください。")

    message = await interaction.channel.send(embed=embed)
    view = EventResponseView(message=message)
    await view.update_message()

    # イベント情報をデータベースに保存
    cursor.execute("INSERT INTO event_info (event_id, message_id, max_participants, recruitment_time, game_name) VALUES (?, ?, ?, ?, ?)",
                   (event.id, message.id, number_of_players, start_time_utc, game_name))
    conn.commit()