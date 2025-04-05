import discord
import config

class TimeSettingModal(discord.ui.Modal, title="採掘時間の設定"):
    hours = discord.ui.TextInput(
        label="採掘時間（時）",
        placeholder="例: 0,12 (カンマ区切りで複数指定可能)",
        required=True
    )
    minutes = discord.ui.TextInput(
        label="採掘時間（分）",
        placeholder="例: 0 (カンマ区切りで複数指定可能)",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # 入力値を数値リストに変換
            hours = [int(h.strip()) for h in self.hours.value.split(",")]
            minutes = [int(m.strip()) for m in self.minutes.value.split(",")]
            
            # 値の検証
            if not all(0 <= h <= 23 for h in hours):
                raise ValueError("時間は0-23の範囲で指定してください")
            if not all(0 <= m <= 59 for m in minutes):
                raise ValueError("分は0-59の範囲で指定してください")
            
            # 設定を更新
            config.ANN_HOUR = hours
            config.ANN_MINUTE = minutes
            
            await interaction.response.send_message(
                f"採掘時間を設定しました\n時間: {hours}\n分: {minutes}",
                ephemeral=True
            )
        except ValueError as e:
            await interaction.response.send_message(
                f"エラー: {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            print(f"時間設定エラー: {e}")
            await interaction.response.send_message(
                "時間設定中にエラーが発生しました",
                ephemeral=True
            ) 