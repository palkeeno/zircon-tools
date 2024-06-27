import os
import random
from datetime import datetime

import discord
from discord.ext import tasks

# made for this prj
import config
import consts.cids as cids
import consts.const as const
import consts.sysmsg as SysMsg
import make_embed
import models.mining as mining
import models.users as users
import util

# init
os.chdir(config.CWD)
intents = discord.Intents.all()
client = discord.Client(intents=intents)


# Bot起動時に呼び出される関数
@client.event
async def on_ready():
    # db作成
    await mining.create_db()
    await users.create_db()
    # 定時アナウンス開始
    check_announce.start()
    print("Ready!")


# 毎日0時を検知して採掘アナウンスを発火
@tasks.loop(seconds=60, reconnect=True)
async def check_announce():
    now = datetime.now(const.JST)
    # 鉱山オープンフラグがFalseならアナウンスが流れない
    if not config.MINE_OPEN:
        return
    if (now.hour in config.ANN_HOUR) and (now.minute in config.ANN_MINUTE):
        await mining.undo_done_flag()
        await send_announce()


# 採掘アナウンスを送信
async def send_announce():
    text = SysMsg.LETS_MINING
    # 採掘ボタン
    button_mine = discord.ui.Button(
        label="採掘",
        style=discord.ButtonStyle.primary,
        custom_id=cids.MINING_ZIRCON,
    )
    # 自分の統計データ表示ボタン
    button_self_stats = discord.ui.Button(
        label="セルフ統計",
        style=discord.ButtonStyle.secondary,
        custom_id=cids.SELF_STATS,
    )
    # 国内の採掘総量表示ボタン
    button_total = discord.ui.Button(
        label="国内サマリ",
        style=discord.ButtonStyle.secondary,
        custom_id=cids.COUNTRY_STATS,
    )
    view = discord.ui.View()
    view.add_item(button_mine)
    view.add_item(button_self_stats)
    view.add_item(button_total)

    channel = client.get_channel(config.CHID_MINING)
    await channel.send(content=text, view=view)


### 国未所属チェックはDiscordチャンネル側で設定


# ジルコン採掘アクション
async def mining_zircon(interaction: discord.Interaction):
    if not config.MINE_OPEN:
        await interaction.response.send_message(
            content=SysMsg.MINE_CLOSED, ephemeral=True
        )
        return
    country = util.get_country(interaction.user)
    # DBのレコードを見て採掘済みかチェック
    ures = await mining.get_user_single(interaction.user.id, country["role"])
    if ures is not None:
        if bool(ures[3]):  # ures[3]=done_flag
            await interaction.response.send_message(
                content=SysMsg.ONCE_MINING, ephemeral=True
            )
            return
    # 採掘ガチャ
    result = util.gacha(random.random(), config.PROBABILITY)
    # 採掘結果がエクセレントかどうか判定
    isExcellent = result["id"] == 0
    # 採掘結果をDBに保存して、メッセージを送信
    await mining.upsert(
        interaction.user.id, country["role"], result["zirnum"], isExcellent
    )
    await users.upsert(interaction.user.id, result["zirnum"], isExcellent)

    # TODO:結果出力embedにガチャ演出を入れる（優先度：中）
    ures = await mining.get_user_single(interaction.user.id, country["role"])
    embed = make_embed.mining(result, interaction.user, ures[2])
    await interaction.response.send_message(embed=embed, ephemeral=True)
    # 採掘結果が「Excellent!!」の場合、各国雑談チャンネルに投稿する
    if isExcellent:
        exc_embed = make_embed.excellent(interaction.user)
        channel = client.get_channel(country["chid"])
        img_ex = discord.File(
        fp=f"{config.CWD}/assets/ex_celebrate.png",
        filename="ex_celebrate.png",
        )
        await channel.send(file=img_ex, embed=exc_embed)


# 自身の統計量（採掘数、採掘回数、Ex数、自身のRank）を表示するアクション
async def get_stats_self(interaction: discord.Interaction):
    country = util.get_country(interaction.user)
    # 基本採掘情報を取得
    result_mining = await mining.get_user_single(interaction.user.id, country["role"])
    result_lifetime = await users.get_single(interaction.user.id)
    if result_lifetime is None:
        await interaction.response.send_message(SysMsg.DATA_NOT_FOUND, ephemeral=True)
        return
    elif result_mining is None:
        result_mining = [int(interaction.user.id), country["id"], 0, 0, 0, 0]
    # 自分のランクを取得
    rank_list = await mining.get_rank_user_country(country["role"])
    res_self = [r for r in rank_list if r[1] == interaction.user.id]
    rank_self = res_self[0][0]
    # embed作成して返信
    embed = make_embed.stats_self(
        result_mining, result_lifetime, interaction.user, rank_self
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# 所属国の統計量（採掘数、採掘回数、ランキングTop10）を表示するアクション
async def get_stats_country(interaction: discord.Interaction):
    country = util.get_country(interaction.user)
    # 国統計データを取得
    result_country = await mining.get_country_single(country["role"])
    if result_country is None:
        result_country = (country["role"], 0, 0)

    # ランク情報の取得
    result_rank = await mining.get_rank_user_country(country["role"])
    # 自分の順位を取得
    res_self = [r for r in result_rank if r[1] == interaction.user.id]
    rank_self = None
    try:
        rank_self = res_self[0][0]
    except IndexError:
        rank_self = 0
    # TOP10を取得
    for index, item in enumerate(result_rank):
        user = interaction.guild.get_member(item[1])
        result_rank[index][1] = user.display_name if user is not None else "None"
        # result_rank[[user_mention1, zirnum1,...], [user_mention2, zirnum2,...],...]

    flag_of_country = discord.File(
        fp=f"{config.CWD}/assets/{country['name']}.jpg",
        filename=f"{country['name']}.jpg",
    )
    embed = make_embed.stats_country(
        result_country, country["name"], result_rank, rank_self
    )
    await interaction.response.send_message(
        file=flag_of_country, embed=embed, ephemeral=True
    )


### 以下は運営コマンド


# 運営向け管理ビュー
async def send_view_to_manage(channel):
    # 国対抗ランキング表示ボタン
    button_rank_country = discord.ui.Button(
        label="国採掘量ランク",
        style=discord.ButtonStyle.secondary,
        custom_id=cids.RANK_COUNTRY,
    )
    # 全ユーザランキングCSV出力ボタン
    button_rank_csv = discord.ui.Button(
        label="ユーザ統計CSV",
        style=discord.ButtonStyle.secondary,
        custom_id=cids.OUTPUT_RANK,
    )
    # 鉱山の営業ステータス確認
    button_mine_status = discord.ui.Button(
        label="鉱山の運営",
        style=discord.ButtonStyle.gray,
        custom_id=cids.MINE_STATUS,
    )
    view = discord.ui.View()
    view.add_item(button_rank_country)
    view.add_item(button_rank_csv)
    view.add_item(button_mine_status)
    await channel.send(view=view)


# 国ごとの採掘量ランキングを取得する
async def get_rank_countries(interaction: discord.Interaction):
    result = await mining.get_country_each()
    result = sorted(
        result, key=lambda x: x[1], reverse=True
    )  # zirnum数の降順に並び替え
    for index, item in enumerate(result):
        result[index][0] = util.get_country_by_roleid(item[0])
    embed = make_embed.rank_country(result)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# 全ユーザのランキングをcsv出力する
async def output_rank_csv(interaction: discord.Interaction):
    dtStr = util.convertDt2Str(datetime.now(const.JST), const.SHORT_DT_FORMAT)
    # 今回の採掘量ランクの出力
    fname_now = const.CSV_FOLDER + "user-rank-now_" + dtStr + const.CSV
    dat_mining = await mining.get_rank_user_overall()
    for index, item in enumerate(dat_mining):
        user = interaction.guild.get_member(item[1]) # メンションIDの取得
        dat_mining[index][1] = user.display_name if user is not None else "None"
        dat_mining[index][2] = user.mention if user is not None else "None"
        country = [c for c in config.COUNTRIES if c["role"] == item[3]]
        dat_mining[index][3] = country[0]["name"]
    util.write_csv(fname_now, const.RANK_HEADER_NOW, dat_mining)

    # 生涯の採掘量ランクの出力
    fname_lt = const.CSV_FOLDER + "user-rank-lifetime_" + dtStr + const.CSV
    dat_users = await users.get_rank(const.LIFETIME)
    for index, item in enumerate(dat_users):
        user = interaction.guild.get_member(item[1]) # メンションIDの取得
        dat_users[index][1] = user.display_name if user is not None else "None"
        dat_users[index][2] = user.mention if user is not None else "None"
    util.write_csv(fname_lt, const.RANK_HEADER_LIFETIME, dat_users)
    await interaction.response.send_message(files=[discord.File(fname_now), discord.File(fname_lt)])


# zircon_numで指定した数だけ、指定したuserに付与
async def add_zircon(user_mention, zircon_num, message):
    target = {"user_id": None, "country": None}
    # 国ユーザの判定
    for c in config.COUNTRIES:
        if c["name"] == str(user_mention):
            target["user_id"] = c["id"]
            target["country"] = c["role"]
    # 一般ユーザの判定
    try:
        mention_str = user_mention.strip("<@!>")
        if target["user_id"] is None and util.isInt(mention_str):
            target["user_id"] = int(mention_str)
            target["country"] = util.get_country(
                message.guild.get_member(target["user_id"])
            )["role"]
        # ターゲットが存在すればジルコンを付与、そうでなければエラーメッセージ送信
        if target["user_id"] is not None and target["country"] is not None:
            await mining.upsert(
                target["user_id"], target["country"], zircon_num, False, False
            )
            await users.upsert(target["user_id"], zircon_num, False, False)
            await message.reply(
                content=f"{user_mention}に{zircon_num} :gem: 付与しました"
            )
        else:
            await message.reply(content=f"ユーザ：{user_mention}は存在しません")
    except BaseException:
        await message.reply(content=f"ユーザ：{user_mention}は存在しません")


# 全イベントの監視
@client.event
async def on_interaction(interaction: discord.Interaction):
    try:
        # component_type=2 : Button
        if interaction.data["component_type"] == 2:
            custom_id = interaction.data["custom_id"]
            if custom_id == cids.MINING_ZIRCON:
                await mining_zircon(interaction)
            elif custom_id == cids.COUNTRY_STATS:
                await get_stats_country(interaction)
            elif custom_id == cids.SELF_STATS:
                await get_stats_self(interaction)
            elif custom_id == cids.RANK_COUNTRY:
                await get_rank_countries(interaction)
            elif custom_id == cids.OUTPUT_RANK:
                await output_rank_csv(interaction)
            elif custom_id == cids.MINE_STATUS:
                status = "OPEN" if config.MINE_OPEN else "CLOSE"
                await interaction.response.send_message(content=status, ephemeral=False)
    except KeyError:
        pass


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel != client.get_channel(config.MCH):
        return
    if message.content == config.DEBUG_CMD:
        # announce manualy
        await send_announce()
        await message.reply(content=SysMsg.MANUAL_ANNOUNCE)
    if message.content == config.RESET_CMD:
        # reset mining database
        await mining.reset_db()
        await message.reply(content=SysMsg.RESET_DB)
    if message.content == config.MNG_CMD:
        # view, rank_role, rank_all
        await send_view_to_manage(message.channel)
    if message.content.startswith(config.ADD_CMD):
        # add zircon to designated user
        args = message.content.split()  # [1]=mention, [2]=num
        if len(args) != 3:
            return
        await add_zircon(args[1], int(args[2]), message)
    if message.content.startswith(config.MSG_CMD):
        # send Management Message to Mining channel as bot
        args = message.content.split()  # [1]=message
        if len(args) < 2:
            return
        ch_mining = client.get_channel(config.CHID_MINING)
        announce_msgs = " ".join(args[1:])
        await ch_mining.send(content=announce_msgs)
    if message.content == config.START_CMD:
        config.MINE_OPEN = True
    if message.content == config.STOP_CMD:
        config.MINE_OPEN = False


# Bot起動
client.run(config.DISCORD_TOKEN)
