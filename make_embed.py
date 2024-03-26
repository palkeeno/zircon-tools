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

# 全国の採掘合計embed
def stats_all(result, country):
    embed = discord.Embed(
        title="各国採掘状況 :pick:",
        description="",
        color=0x0000ff
    )
    for c in country:
        flg = 0
        for res in result:
            if c['role'] == res[0]:
                zirnum = int(res[1])
                embed.add_field(
                    name=f"{c['stmp']} {c['name']} : {zirnum} :gem:", 
                    value="", 
                    inline=False
                )
                flg = 1
                break

        # 結果がまだない国は0個で表示
        if flg == 0:
            embed.add_field(
                name=f"{c['stmp']} {c['name']} : 0 :gem:", 
                value="", 
                inline=False
            )
    return embed

