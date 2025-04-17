# discord.pyのapp_commandsをインポート
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
    def __init__(self, interaction: discord.Interaction, game_name: str, number_of_players: int, start_time_utc: datetime, channel: discord.VoiceChannel):
        super().__init__(timeout=None)
        self.yes_users = set()
        self.no_users = set()
        self.interaction = interaction 
        self.game_name = game_name 
        self.number_of_players = number_of_players 
        self.start_time_utc = start_time_utc
        self.channel = channel
        self.message = None

    async def update_message(self):
        if not self.message:
            # Discordのスケジュールイベントを作成
            self.event = await self.interaction.guild.create_scheduled_event(
                name=f"{self.game_name}募集 @{self.number_of_players}",
                description=f"募集中",
                start_time=self.start_time_utc,
                channel=self.channel,
                entity_type=discord.EntityType.voice,
                privacy_level=discord.PrivacyLevel.guild_only
            )

            # 埋め込みメッセージを作成
            tokyo_tz = timezone(timedelta(hours=9))
            embed = Embed(title=f"{self.game_name}募集 @{self.number_of_players}", description=f"[イベントリンク]({self.event.url})", color=0x3498db)
            embed.add_field(name="開始時間", value=self.start_time_utc.astimezone(tokyo_tz).strftime("%H:%M"), inline=True)
            embed.add_field(name="ボイスチャンネル", value=self.channel.mention, inline=True)
            embed.add_field(name="参加者リスト", value="", inline=False)
            embed.set_footer(text="ボタンをクリックして参加状況を更新してください。")
            self.message = await self.interaction.channel.send(embed=embed)
        else:
            embed = self.message.embeds[0]  # 既存の埋め込みメッセージを取得
            # 参加者リストを更新
            update_field_by_partial_name(embed, "参加可能", len(self.yes_users), "\n".join(map(lambda user_id: f"<@{user_id}>", self.yes_users)) or "なし", inline=False)
            update_field_by_partial_name(embed, "参加不可", len(self.no_users), "\n".join(map(lambda user_id: f"<@{user_id}>", self.no_users)) or "なし", inline=False)
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

                # 埋め込みメッセージを更新
                embed = self.message.embeds[0]  # 既存の埋め込みメッセージを取得
                embed.title = f"{embed.title}  〆"
                embed.color = 0x808080
                await self.message.edit(embed=embed, view=self)

                # Discordのスケジュールイベントを更新
                try:
                    event = await interaction.guild.fetch_scheduled_event(self.event.id)
                    await event.edit(name=f"{event.name} 〆", description="募集完了")
                except Exception as e:
                    print(f"Error updating event: {e}")

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

__all__ = ["EventResponseView"]