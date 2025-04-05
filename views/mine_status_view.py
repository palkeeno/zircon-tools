import discord
import config

def mine_status(isMineOpen):
    return "OPEN" if isMineOpen else "CLOSE"

class MineStatusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="OPEN", style=discord.ButtonStyle.green)
    async def open_mine(self, interaction: discord.Interaction, button: discord.ui.Button):
        config.MINE_OPEN = True
        await interaction.response.send_message(mine_status(True), ephemeral=True)
        
    @discord.ui.button(label="CLOSE", style=discord.ButtonStyle.red)
    async def close_mine(self, interaction: discord.Interaction, button: discord.ui.Button):
        config.MINE_OPEN = False
        await interaction.response.send_message(mine_status(False), ephemeral=True) 