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
        title=f"{country['name']}国",
        description="",
        color=0x0000ff
    )
    embed.set_thumbnail(url=f"attachment://{country['name']}.jpg")
    embed.add_field(
        name="総採掘ジルコン :gem:", value=f"{int(result[1])}", inline=True
    )
    embed.add_field(
        name="参加回数 :pick:", value=f"{int(result[2])}", inline=True
    )
    return embed

# 自分の採掘合計embed
def stats_self(result, usr):
    embed = discord.Embed(
        title="",
        description="",
        color=0x0000ff
    )
    embed.set_author(name=f"{usr.display_name}", icon_url=usr.display_avatar.url)
    embed.add_field(
        name="採掘量 :gem:", value=f"{int(result[2])}", inline=True
    )
    embed.add_field(
        name="採掘回数 :pick:", value=f"{int(result[4])}", inline=True
    )
    embed.add_field(
        name="Excellent回数 :tada:", value=f"{int(result[5])}", inline=True
    )
    return embed

# ユーザーランキングの表示embed
def rank_role(result, res_self, cName, usr):
    embed = discord.Embed(
        title=f"{cName}国内 ランキングTOP10",
        description=f"Your Rank: {res_self[0]} th",
        color=0x00ffff
    )
    embed.set_author(name=f"{usr.display_name}", icon_url=usr.display_avatar.url)
    # result[[user_mention1, zirnum1,...], [user_mention2, zirnum2,...],...]
    for index in range(min(10, len(result))):
        embed.add_field(
            name="",
            value=f"**`{result[index][0]}.`** {result[index][1]} • :gem: {result[index][2]}",
            inline=False
        )
    return embed

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