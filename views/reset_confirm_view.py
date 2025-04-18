import discord
import models.mining as mining
import models.users as users

class ResetConfirmView(discord.ui.View):
    def __init__(self, reset_type: str):
        super().__init__(timeout=None)
        self.reset_type = reset_type
        
    @discord.ui.button(label="はい", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.reset_type == "mining":
                await mining.reset_db()
                await interaction.response.send_message("採掘DBをリセットしました", ephemeral=False)
            else:
                await mining.reset_db()
                await users.reset_db()
                await interaction.response.send_message("すべてのDBをリセットしました", ephemeral=False)
        except Exception as e:
            print(f"DBリセットエラー: {e}")
            await interaction.response.send_message("DBリセット中にエラーが発生しました", ephemeral=False)
        
    @discord.ui.button(label="いいえ", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("リセットをキャンセルしました", ephemeral=False) 