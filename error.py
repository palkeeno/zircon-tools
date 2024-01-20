import config
import discord

E001_INVALID_CHANNEL = {'code':'001', 'msg':"Error 001: Invalid channel to use this command"}
E002_INVALID_ROLE = {'code':'002', 'msg':"Error 002: Invalid roles"}
E003_DATA_NOT_FOUND = {'code':'003', 'msg':"Error 003: Data not found"}

async def check_invalid_minor(interaction: discord.Interaction, country):
    # 国ロールがない場合はエラー
    if country == None:
        await interaction.response.send_message(E002_INVALID_ROLE['msg'], ephemeral=True)
        return True
    # 採掘チャンネル以外ではエラー
    if interaction.channel_id != config.CHID_MINING:
        await interaction.response.send_message(E001_INVALID_CHANNEL['msg'], ephemeral=True)
        return True
    return False
    
