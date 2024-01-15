import discord
from discord import app_commands
from discord.ext import tasks
import random
from datetime import time, timezone, timedelta, datetime
# made for this prj
import config
import make_embed
import model
import util
import error

# init
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
cooldown_obj = app_commands.Cooldown(1, config.CD_MINING) # クールダウン用オブジェクト
JST = timezone(timedelta(hours=+9), "JST")

# Bot起動時に呼び出される関数
@client.event
async def on_ready():
    # db作成
    await model.create_zmdb()
    # スラッシュコマンドを起動
    await tree.sync()
    # 定時アナウンス開始
    mine_announce.start()
    print("Ready!")

# クールダウンチェック用のオブジェクト、
def cooldown_checker(interaction: discord.Interaction):
    return cooldown_obj

# 毎日0時の採掘アナウンス
@tasks.loop(seconds=60, reconnect=True)
async def mine_announce():
    now = datetime.now(JST)
    if now.hour == 0 and now.minute == 0:
        # メッセージ作成部
        text = config.MSG_LETS_MINING
        # 採掘ボタン
        button_mine = discord.ui.Button(
            label="ジルコン採掘",
            style=discord.ButtonStyle.primary,
            custom_id="mining_zircon")
        # 採掘量表示ボタン（引数＝all）
        button_total = discord.ui.Button(
            label="各国採掘量",
            style=discord.ButtonStyle.secondary,
            custom_id="total_all"
        )
        view = discord.ui.View()
        view.add_item(button_mine)
        view.add_item(button_total)
        # 送信処理
        channel = client.get_channel(config.CHID_MINING)
        await channel.send(content=text, view=view)

# @tree.command(name="zircon", description="ジルコン採掘をします")
@app_commands.checks.dynamic_cooldown(cooldown_checker)
async def slash_zircon(interaction: discord.Interaction):
    country = util.get_country(interaction.user)
    # ロールとチャンネルをチェック
    if await error.check_invalid_minor(interaction, country):
        # 不適格であったら、クールダウンをリセットして終了
        app_commands.Cooldown.reset(cooldown_obj)
        return
    # DBから採掘済みかチェック
    ures = model.select_zm_user(interaction.user.id, country['id'])
    latest_updated = datetime.fromtimestamp(ures[3], JST).date()
    now = datetime.now(JST).date()
    if latest_updated == now :
        # 採掘済みなら、また明日来るように伝えて終了
        await interaction.response.send_message(content=config.MSG_ONCE_MINING, ephemeral=True)
        return
    # 採掘結果を出す
    result = util.gacha(random.random(), config.RESULTS)
    embed = make_embed.mining(country, result, interaction.user)
    # データを保存
    await model.insert_zm(interaction.user.id, country['id'], result['zirnum'])
    # メッセージを送信
    await interaction.response.send_message(embed=embed, ephemeral=True)

# @tree.command(name="total", description="自国の採掘総量を確認します。引数に all 指定で4か国分表示します。")
async def slash_total(interaction: discord.Interaction, all:str=""):
    country = util.get_country(interaction.user)
    # ロールとチャンネルをチェック
    if await error.check_invalid_minor(interaction, country):
        # 不適格なら終了
        return
    # "all"付きなら4か国分、そうでないなら自国分
    if all == "all":
        result = await model.select_total_all_role()
        if result == None:
            await interaction.response.send_message(error.E003_DATA_NOT_FOUND['msg'], ephemeral=True)
            return
        embed = make_embed.stats_all(result, config.COUNTRIES)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        # 発火者のロールを参照して採掘合計を返す、結果がNoneの場合は無視
        result = await model.select_total_by_role(country['id'])
        if result == None:
            result = (country['id'], 0)
        embed = make_embed.stats_role(result[1], country)
        await interaction.response.send_message(file=country['img'], embed=embed, ephemeral=True)

# 全イベントの監視
# ボタン押下の検知->採掘
@client.event
async def on_interaction(interaction: discord.Interaction):
    try:
        if interaction.data['component_type'] == 2:
            custom_id = interaction.data['custom_id']
            if custom_id == "mining_zircon":
                await slash_zircon(interaction)
            elif custom_id == "total_all":
                await slash_total(interaction, "all")
    except KeyError:
        pass

# エラー時の処理
@tree.error
async def on_command_error(interaction, err):
    if isinstance(err, app_commands.CommandOnCooldown):
        await error.catch_cooldown(interaction, int(err.retry_after))

# Bot起動
client.run(config.DISCORD_TOKEN)