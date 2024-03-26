import discord

# 採掘結果のembed
def mining(country, result, usr):
    embed = discord.Embed(
        title="",
        description="",
        color=0x00ff00
    )
    embed.set_author(name=usr.display_name, icon_url=usr.display_avatar.url)
    embed.add_field(
        name=f"採掘結果 :pick: : {result['msg']}", 
        value=f"{country['name']} {country['stmp']} : + **{result['zirnum']}** ジルコン :gem:", 
        inline=False
    )
    return embed

# 採掘結果Excellentを雑談チャネルに投稿するときのembed
def excellent(usr):
    embed = discord.Embed(
        title="Excellent採掘しました！ :gem::gem::gem:",
        description="",
        color=0x00ff00
    )
    embed.set_author(name=usr.display_name, icon_url=usr.display_avatar.url)

    return embed

# 1国分の採掘合計embed
def stats_role(result, country):
    embed = discord.Embed(
        title=f"{int(result[1])} :gem:",
        description="",
        color=0x0000ff
    )
    embed.set_author(name=f"{country['name']}国の総採掘量")
    embed.set_thumbnail(url=f"attachment://{country['name']}.jpg")
    embed.add_field(
        name="", 
        value=f"総採掘回数 : {int(result[2])}", 
        inline=False
    )
    return embed

# 自分の採掘合計embed
def stats_self(result, usr):
    embed = discord.Embed(
        title=f"{result[2]} :gem:",
        description="",
        color=0x0000ff
    )
    embed.set_author(name=f"{usr.display_name} の採掘量", icon_url=usr.display_avatar.url)
    embed.add_field(
        name="", 
        value=f"採掘回数 : {result[4]}", 
        inline=False
    )
    return embed

# ユーザーランキングの表示embed
def rank_role(result, cName):
    embed = discord.Embed(
        title=f"{cName}国 Ranking",
        description="",
        color=0x00ffff
    )
    # result[[user_name1, zirnum1,...], [user_name2, zirnum2,...],...]
    for index, item in enumerate(result):
        embed.add_field(
            name="",
            value=f"**{index}.** {item[0]} • :gem: {item[1]}",
            inline=False
        )

# 国対抗ランキングのembed
def rank_country(result):
    embed = discord.Embed(
        title="国対抗ランキング",
        description="",
        color=0x0000ff
    )
    for rank, res in enumerate(result):
        embed.add_field(
            name=f"{rank+1} : {res[0]['stmp']} {res[0]['name']} : {res[1]} :gem:",
            value="",
            inline=False
        )
    return embed