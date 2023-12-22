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

# 1国分の採掘合計embed
def stats_role(result, country):
    embed = discord.Embed(
        title="",
        description="",
        color=0x0000ff
    )
    embed.set_author(name=country['name'])
    embed.set_thumbnail(url=f"attachment://{country['name']}.jpg")
    embed.add_field(
        name=f"ジルコン採掘合計 :gem: : {result}", 
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
                    name=f"{c['name']} {c['stmp']} : {zirnum} ジルコン", 
                    value="", 
                    inline=False
                )
                flg = 1
                break

        # 結果がまだない国は0個で表示
        if flg == 0:
            embed.add_field(
                name=f"{c['name']} {c['stmp']} : 0 ジルコン", 
                value="", 
                inline=False
            )
    return embed
