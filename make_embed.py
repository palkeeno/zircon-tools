import discord
from util import ordinal

# 採掘結果のembed
def mining(result, usr, total):
    embed = discord.Embed(
        title="",
        description="",
        color=0x00ff00
    )
    embed.set_author(name=usr.display_name, icon_url=usr.display_avatar.url)
    embed.add_field(
        name=f":pick: :sparkles: {result['msg']}! **{result['zirnum']}** :gem: 掘れた！", 
        value=f"", 
        inline=False
    )
    embed.add_field(
        name=f"",
        value=f"これまでの採掘数 **{total}** :gem:",
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

# 指定国の統計データembed(ジェム数、採掘回数、自分のランク、Top10)
def stats_country(res_country, country_name, res_rank, rank_self):
    rank = ordinal(rank_self) if rank_self != 0 else 'None'
    embed = discord.Embed(
        title=f"{country_name}国 サマリ",
        description="",
        color=0x0000ff
    )
    embed.set_thumbnail(url=f"attachment://{country_name}.jpg")
    # 統計データ表示
    embed.add_field(
        name=f"""
ジルコン : {int(res_country[1])} :gem:
採掘回数 : {int(res_country[2])} :pick:
        """,
        value=f"",
        inline=False
    )

    # ランキング表示
    embed.add_field(
        name=f"ランキングTOP10",
        value=f"Your Rank: {rank}",
        inline=False
    )
    # res_rank[[user_mention1, zirnum1,...], [user_mention2, zirnum2,...],...]
    top10List = []
    for index in range(min(10, len(res_rank))):
        top10List.append(f"**{res_rank[index][0]}.** `{res_rank[index][1]}` • :gem: {res_rank[index][2]}")
    top10Str = "\n\r".join(top10List)

    embed.add_field(
        name="",
        value=f"{top10Str}",
        inline=False
    )
    return embed

# 自分の統計データembed(ジェム数、採掘回数、Ex数、国内順位)
def stats_self(result_mining, result_lifetime, usr, rank_self):
    rank = ordinal(rank_self) if rank_self != 0 else 'None'
    embed = discord.Embed(
        title="",
        description="",
        color=0x0000ff
    )
    embed.set_author(name=f"{usr.display_name} 採掘データ", icon_url=usr.display_avatar.url)

    embed.add_field(
        name=f"""
ジルコン : {int(result_mining[2])} :gem: （累積 {int(result_lifetime[2])}）
採掘回数 : {int(result_mining[4])} :pick: （累積 {int(result_lifetime[3])}）
Excellent : {int(result_mining[5])} :tada: （累積 {int(result_lifetime[4])}）
        """,
        value=f"国内順位 {rank}",
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