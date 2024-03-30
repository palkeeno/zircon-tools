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
        label="採掘",
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
    # 国ごとにユーザの採掘量ランキングを表示（各10位まで＋自分の順位）
    button_rank_role = discord.ui.Button(
        label="国内ランキング",
        style=discord.ButtonStyle.success,
        custom_id="rank_user"
    )
    view = discord.ui.View()
    view.add_item(button_mine)
    view.add_item(button_sum_self)
    view.add_item(button_total)
    view.add_item(button_rank_role)

    channel = client.get_channel(config.CHID_MINING)
    await channel.send(content=text, view=view)

# ジルコン採掘アクション
async def mining_zircon(interaction: discord.Interaction):
    country = util.get_country(interaction.user)
    if error.check_country(country):
        await interaction.response.send_message(content=constants.MSG_COUNTRY_ROLE, ephemeral=True)
        return
    # DBのレコードを見て採掘済みかチェック
    ures = await model.get_user_result(interaction.user.id, country['role'])
    if ures != None:
        if bool(ures[3]) : # ures[3]=done_flag
            await interaction.response.send_message(content=constants.MSG_ONCE_MINING, ephemeral=True)
            return
    # 採掘結果を出す
    result = util.gacha(random.random(), config.PROBABILITY)
    embed = make_embed.mining(country, result, interaction.user)
    isExcellent = (result['id'] == 0) # 採掘結果がエクセレントかどうか判定
    # 採掘結果をDBに保存して、メッセージを送信
    await model.upsert_mining(interaction.user.id, country['role'], result['zirnum'], isExcellent)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    # 採掘結果が「Excellent!!」の場合、各国雑談チャンネルに投稿する
    if isExcellent:
        exc_embed = make_embed.excellent(interaction.user)
        channel = client.get_channel(country['chid'])
        await channel.send(embed=exc_embed)

# 採掘量を表示するアクション
### args = self :現在の所属国での自分の採掘量
### args = single :現在の所属国の全体採掘量
async def get_stats(interaction: discord.Interaction, arg:str=""):
    country = util.get_country(interaction.user)
    if error.check_country(country):
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

# 管理ビュー（運営向け）
async def send_view_to_manage(channel):
    # 国対抗ランキング表示ボタン
    button_rank_country = discord.ui.Button(
        label="国対抗ランキング表示",
        style=discord.ButtonStyle.secondary,
        custom_id="rank_country"
    )
    # 全ユーザランキングCSV出力ボタン
    button_rank_csv = discord.ui.Button(
        label="ランキングCSV出力",
        style=discord.ButtonStyle.secondary,
        custom_id="rank_csv"
    )
    view = discord.ui.View()
    view.add_item(button_rank_country)
    view.add_item(button_rank_csv)
    await channel.send(view=view)

# 採掘量ランキングを取得する
### args = user_role:ユーザの国ごとranking(ユーザコマンド)
### args = country_all:国ごとのranking(運営コマンド)
async def get_rank(interaction: discord.Interaction, args=""):
    now = datetime.now()
    if args == "user_role":
        country = util.get_country(interaction.user)
        if error.check_country(country):
            await interaction.response.send_message(content=constants.MSG_COUNTRY_ROLE, ephemeral=True)
            return
        result = await model.get_user_rank_role(country['role'])
        # 自分の順位を取得
        res_self = [r for r in result if r[1] == interaction.user.id]
        rank_self = None
        try:
            rank_self = res_self[0][0]
        except IndexError:
            rank_self = 0
        # TOP10を取得
        for index, item in enumerate(result):
            user = interaction.guild.get_member(item[1])
            result[index][1] = user.display_name # [0]=rank, [1]=user_name, [2]=zirnum
        embed = make_embed.rank_role(result, rank_self, country['name'], interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif args == "country_all":
        result = await model.get_total_all_countries()
        result = sorted(result, key=lambda x: x[1], reverse=True) # zirnum数の降順に並び替え
        for index, item in enumerate(result):
            result[index][0] = util.get_country_by_roleid(item[0])
        embed = make_embed.rank_country(result)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# 全ユーザのランキングをcsv出力する（運営コマンド）
async def output_rank_csv(interaction: discord.Interaction):
    dtStr = util.convertDt2Str(datetime.now(constants.JST), constants.SHORT_DT_FORMAT)
    filename = constants.CSV_FOLDER+"user-rank_"+dtStr+constants.CSV
    data =  await model.get_user_rank_overall()
    for index, item in enumerate(data):
            user = interaction.guild.get_member(item[1])
            data[index][1] = user.display_name
            country = [ c for c in config.COUNTRIES if c['role'] == item[3]]
            data[index][3] = country[0]['name']
            data[index][6] = user.mention
    util.write_csv(filename, constants.RANK_HEADER, data)
    await interaction.response.send_message(file=discord.File(filename))

# zircon_numで指定した数だけ、指定したuserに付与
async def add_zircon(user_mention, zircon_num, message):
    target = {'user_id':None, 'country':None}
    # 国ユーザの判定
    for c in config.COUNTRIES:
        if c['name'] == str(user_mention):
            target['user_id'] = c['id']
            target['country'] = c['role']
    # 一般ユーザの判定
    try:
        mention_str = user_mention.strip('<@!>')
        if target['user_id'] == None and util.isInt(mention_str) :
            target['user_id'] = int(mention_str)
            target['country'] = util.get_country(message.guild.get_member(target['user_id']))['role']
        # ターゲットが存在すればジルコンを付与、そうでなければエラーメッセージ送信
        if target['user_id'] != None and target['country'] != None:
            await model.add_zirnum(target['user_id'], target['country'], zircon_num)
            await message.reply(content=f"{user_mention}に{zircon_num} :gem: 付与しました")
        else: 
            await message.reply(content=f"ユーザ：{user_mention}は存在しません")
    except: 
        await message.reply(content=f"ユーザ：{user_mention}は存在しません")

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
            elif custom_id == "rank_user":
                await get_rank(interaction, "user_role")
            elif custom_id == "rank_country":
                await get_rank(interaction, "country_all")
            elif custom_id == "rank_csv":
                await output_rank_csv(interaction)
    except KeyError:
        pass

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel != client.get_channel(config.MCH):
        return
    if message.content == config.DEBUG_CMD:
        # announce yourself
        await send_announce()
        await message.reply(content="アナウンスを発動しました")
    if message.content == config.RESET_CMD:
        # reset mining database
        await model.reset_zmdb()
        await message.reply(content="データベースをリセットしました")
    if message.content == config.MNG_CMD:
        # view, rank_role, rank_all
        await send_view_to_manage(message.channel)
    if message.content.startswith(config.ADD_CMD):
        # add zircon to designated user
        args = message.content.split() # [1]=mention, [2]=num
        if len(args) != 3:
            return
        await add_zircon(args[1], int(args[2]), message)
    if message.content.startswith(config.MSG_CMD):
        # send Management Message to Mining channel as bot
        args = message.content.split() # [1]=message
        if len(args) != 2:
            return
        ch_msg = client.get_channel(config.CHID_MINING)
        await ch_msg.send(content=args[1])

# Bot起動
client.run(config.DISCORD_TOKEN)