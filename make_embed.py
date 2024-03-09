import discord

# 採掘結果のembed
def mining(country, result, usr):
    embed = discord.Embed(
        title="",
        description="",
        color=0x00ff00
    )
    embed.set_author(name=usr.name, icon_url=usr.avatar.url)
    embed.add_field(
        name=f"採掘結果 :pick: : {result['msg']}", 
        value=f"{country['name']} {country['stmp']} : + **{result['zirnum']}** ジルコン :gem:", 
        inline=False
    )
    return embed

# 採掘結果Excellentを雑談チャネルに投稿するときのembed
def excellent(usr):
    embed = discord.Embed(
        title="Excellent発掘しました！ :gem::gem::gem:",
        description="",
        color=0x00ff00
    )
    embed.set_author(name=usr.name, icon_url=usr.avatar.url)

    return embed

# 1国分の採掘合計embed
def stats_role(result, country):
    embed = discord.Embed(
        title="自国の採掘量",
        description="",
        color=0x0000ff
    )
    embed.set_author(name=country['name'])
    embed.set_thumbnail(url=f"attachment://{country['name']}.jpg")
    embed.add_field(
        name=f"ジルコン採掘合計 :gem: : {result[1]}", 
        value="", 
        inline=False
    )
    return embed

# 自分の採掘合計embed
def stats_self(result, usr):
    embed = discord.Embed(
        title="",
        description="所属国でのあなたの採掘量は...",
        color=0x0000ff
    )
    embed.set_author(name=usr.name, icon_url=usr.avatar.url)
    embed.add_field(
        name=f"{result[2]} :gem:", 
        value="", 
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
            if c['id'] == res[0]:
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

