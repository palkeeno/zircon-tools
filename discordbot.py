import discord
from discord.ext import tasks
import random
from datetime import datetime
# made for this prj
import config
import constants
import make_embed
import model
import util
import error

# init
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Bot起動時に呼び出される関数
@client.event
async def on_ready():
    # db作成
    await model.create_zmdb()
    # 定時アナウンス開始
    check_announce.start()
    print("Ready!")

# 毎日0時を検知して採掘アナウンスを発火
@tasks.loop(seconds=60, reconnect=True)
async def check_announce():
    now = datetime.now(constants.JST)
    if (now.hour in config.ANN_HOUR) and (now.minute in config.ANN_MINUTE):
        await model.unflag_mining()
        await send_announce()

# 採掘アナウンスを送信
async def send_announce():
    text = constants.MSG_LETS_MINING
    # 採掘ボタン
    button_mine = discord.ui.Button(
        label="ジルコン採掘",
        style=discord.ButtonStyle.primary,
        custom_id="mining_zircon")
    # 自分の採掘量表示ボタン
    button_sum_self = discord.ui.Button(
        label="あなたの採掘量",
        style=discord.ButtonStyle.secondary,
        custom_id="sum_self"
    )
    # 国内の採掘総量表示ボタン
    button_total = discord.ui.Button(
        label="国内合計",
        style=discord.ButtonStyle.secondary,
        custom_id="total_single"
    )
    view = discord.ui.View()
    view.add_item(button_mine)
    view.add_item(button_sum_self)
    view.add_item(button_total)

    channel = client.get_channel(config.CHID_MINING)
    await channel.send(content=text, view=view)

# ジルコン採掘アクション
async def mining_zircon(interaction: discord.Interaction):
    country = util.get_country(interaction.user)
    if await error.check_country(interaction, country):
        await interaction.response.send_message(content=constants.MSG_COUNTRY_ROLE, ephemeral=True)
        return
    # DBのレコードを見て採掘済みかチェック
    ures = await model.get_user_result(interaction.user.id, country['role'])
    if ures != None:
        if bool(ures[3]) : # ures[3]=done_flag
            await interaction.response.send_message(content=constants.MSG_ONCE_MINING, ephemeral=True)
            return
    # 採掘結果を出す
    result = util.gacha(random.random(), config.RESULTS)
    embed = make_embed.mining(country, result, interaction.user)
    # 採掘結果をDBに保存して、メッセージを送信
    await model.upsert_mining(interaction.user.id, country['role'], result['zirnum'])
    await interaction.response.send_message(embed=embed, ephemeral=True)
    # 採掘結果が「Excellent!!」の場合、各国雑談チャンネルに投稿する
    if result['id'] == 0:
        exc_embed = make_embed.excellent(interaction.user)
        channel = client.get_channel(country['chid'])
        await channel.send(embed=exc_embed)

async def get_stats(interaction: discord.Interaction, arg:str=""):
    country = util.get_country(interaction.user)
    if await error.check_country(interaction, country):
        await interaction.response.send_message(content=constants.MSG_COUNTRY_ROLE, ephemeral=True)
        return
    # 引数によってとる内容を出し分け、結果がNoneの場合は無視
    if arg == "self":
        result = await model.get_user_result(interaction.user.id, country['role'])
        if result == None:
            await interaction.response.send_message(error.E003_DATA_NOT_FOUND['msg'], ephemeral=True)
            return
        embed = make_embed.stats_self(result, interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif arg == "single":
        result = await model.get_total_single_country(country['role'])
        if result == None:
            result = (country['role'], 0)
        embed = make_embed.stats_role(result, country)
        await interaction.response.send_message(file=country['img'], embed=embed, ephemeral=True)

# 4国すべての採掘状況を表示（運営向け）
async def get_all(interaction: discord.Interaction):
    result = await model.select_total_all_country()
    if result == None:
        await interaction.response.send_message(error.E003_DATA_NOT_FOUND['msg'], ephemeral=True)
        return
    embed = make_embed.stats_all(result, config.COUNTRIES)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 呼び出した人だけが押せるボタン（運営向け）
async def send_view_to_manage(channel):
    # 4国すべての採掘量表示ボタン
    button_total = discord.ui.Button(
        label="4国状況",
        style=discord.ButtonStyle.secondary,
        custom_id="total_all"
    )
    view = discord.ui.View()
    view.add_item(button_total)

    await channel.send(view=view)

# ユーザランクを10位まで表示する, args=roleで国ごと、allで全国
async def get_rank_role(interaction: discord.Interaction, args=""):
    result = None
    if args == "role":
        for country in config.COUNTRIES:
            result = await model.get_user_rank(country["id"], 10)
    elif args == "all":
        result = await model.get_user_rank_overall(10)
    return result

# zircon_numで指定した数だけ、userに付与
async def add_zircon(user_mention, zircon_num, m_guild):
    user_id = int(user_mention.strip('<@!>'))
    country = util.get_country(m_guild.get_member(user_id))
    await model.upsert_mining(user_id, country['role'], zircon_num)

# 全イベントの監視
# ボタン押下の検知->採掘
@client.event
async def on_interaction(interaction: discord.Interaction):
    try:
        if interaction.data['component_type'] == 2:
            custom_id = interaction.data['custom_id']
            if custom_id == "mining_zircon":
                await mining_zircon(interaction)
            elif custom_id == "total_single":
                await get_stats(interaction, "single")
            elif custom_id == "sum_self":
                await get_stats(interaction, "self")
            elif custom_id == "total_all":
                await get_all(interaction)
    except KeyError:
        pass

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel != client.get_channel(config.MCH):
        return
    if message.content == config.DEBUG_CMD:
        await send_announce()
        await message.reply(content="アナウンスを発動しました")
    if message.content == config.RESET_CMD:
        await model.reset_zmdb()
        await message.reply(content="データベースをリセットしました")
    if message.content == config.VIEW_CMD:
        await send_view_to_manage(message.channel)
    if message.content.startswith(config.ADD_CMD):
        args = message.content.split() # [1]=mention, [2]=num
        if len(args) != 3:
            return
        await add_zircon(args[1], int(args[2]), message.guild)
        await message.reply(content=f'{args[1]}に{args[2]}ジルコン付与しました')

# Bot起動
client.run(config.DISCORD_TOKEN)