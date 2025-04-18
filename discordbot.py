import asyncio
import os
import random
from datetime import datetime

import discord
from discord.ext import tasks
from discord import app_commands

# made for this prj
import config
import consts.cids as cids
import consts.characters as characters
from consts.characters import get_random_character
import consts.const as const
import consts.sysmsg as SysMsg
import make_embed
import models.mining as mining
import models.users as users
import util
from views import MineStatusView, RankView, ResetConfirmView
from models.backup_utils import perform_backup

# init
os.chdir(config.CWD)
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 管理チャンネルチェック
def is_admin_channel():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.channel_id == config.MCH
    return app_commands.check(predicate)

# スラッシュコマンドの定義
@tree.command(name="zmst", description="鉱山の営業状況を表示・変更します")
@is_admin_channel()
async def zmst(interaction: discord.Interaction):
    view = MineStatusView()
    await interaction.response.send_message(
        f"現在の営業状況: {mine_status(config.MINE_OPEN)}\n変更する場合は下のボタンを押してください。",
        view=view,
        ephemeral=False
    )

@tree.command(name="zmrank", description="ランキング情報を表示します")
@is_admin_channel()
async def zmrank(interaction: discord.Interaction):
    view = RankView()
    await interaction.response.send_message(
        "表示するランキングを選択してください：",
        view=view,
        ephemeral=False
    )

@tree.command(name="zmadd", description="指定したユーザーにジルコンを付与します")
@is_admin_channel()
async def zmadd(interaction: discord.Interaction, amount: int, user: discord.Member):
    try:
        country = util.get_country(user)
        await mining.upsert(user.id, country["role"], amount, False)
        await users.upsert(user.id, amount, False)
        await interaction.response.send_message(
            f"{user.mention}に{amount} :gem: 付与しました",
            ephemeral=False
        )
    except Exception as e:
        print(f"ジルコン付与エラー: {e}")
        await interaction.response.send_message(
            "ジルコン付与中にエラーが発生しました。",
            ephemeral=False
        )

@tree.command(name="zmmsg", description="採掘チャンネルにメッセージを投稿します")
@is_admin_channel()
async def zmmsg(interaction: discord.Interaction, message: str):
    try:
        channel = client.get_channel(config.CHID_MINING)
        await channel.send(content=message)
        await interaction.response.send_message(f"メッセージを投稿しました\n投稿内容：{message}", ephemeral=False)
    except Exception as e:
        print(f"メッセージ投稿エラー: {e}")
        await interaction.response.send_message(
            "メッセージの投稿中にエラーが発生しました。",
            ephemeral=False
        )

@tree.command(name="zmannounce", description="採掘アナウンスを手動で送信します")
@is_admin_channel()
async def zmannounce(interaction: discord.Interaction):
    try:
        await send_announce()
        await interaction.response.send_message("アナウンスを送信しました", ephemeral=False)
    except Exception as e:
        print(f"アナウンス送信エラー: {e}")
        await interaction.response.send_message(
            "アナウンスの送信中にエラーが発生しました。",
            ephemeral=False
        )

@tree.command(name="zmreset", description="データベースをリセットします")
@is_admin_channel()
async def zmreset(interaction: discord.Interaction, reset_type: str):
    if reset_type not in ["mining", "all"]:
        await interaction.response.send_message(
            "無効なリセットタイプです。'mining'または'all'を指定してください。",
            ephemeral=False
        )
        return
        
    view = ResetConfirmView(reset_type)
    await interaction.response.send_message(
        f"{'採掘DB' if reset_type == 'mining' else 'すべてのDB'}をリセットしますか？",
        view=view,
        ephemeral=False
    )

@tree.command(name="zmtime", description="採掘時間を設定します")
@is_admin_channel()
async def zmtime(interaction: discord.Interaction, hours: str = None, minutes: str = None):
    # 引数なしの場合は現在の設定を表示
    if hours is None and minutes is None:
        current_hours = config.ANN_HOUR
        current_minutes = config.ANN_MINUTE
        
        # 時間を整形して表示
        hours_str = ", ".join(map(str, current_hours))
        minutes_str = ", ".join(map(str, current_minutes))
        
        await interaction.response.send_message(
            f"現在の採掘時間設定:\n時間: {hours_str}\n分: {minutes_str}\n\n"
            f"時間を設定するには、`/zmtime 時間 分` の形式で入力してください。\n"
            f"例: `/zmtime 0,12 0` (0時と12時に設定)",
            ephemeral=False
        )
        return
    
    # 引数がある場合は直接設定
    try:
        # 入力値を数値リストに変換
        hours_list = [int(h.strip()) for h in hours.split(",")]
        minutes_list = [int(m.strip()) for m in minutes.split(",")]
        
        # 値の検証
        if not all(0 <= h <= 23 for h in hours_list):
            raise ValueError("時間は0-23の範囲で指定してください")
        if not all(0 <= m <= 59 for m in minutes_list):
            raise ValueError("分は0-59の範囲で指定してください")
        
        # 設定を更新
        config.ANN_HOUR = hours_list
        config.ANN_MINUTE = minutes_list
        
        await interaction.response.send_message(
            f"採掘時間を設定しました\n時間: {hours_list}\n分: {minutes_list}",
            ephemeral=False
        )
    except ValueError as e:
        await interaction.response.send_message(
            f"エラー: {str(e)}",
            ephemeral=False
        )
    except Exception as e:
        print(f"時間設定エラー: {e}")
        await interaction.response.send_message(
            "時間設定中にエラーが発生しました",
            ephemeral=False
        )

@tree.command(name="zmhelp", description="運営向けのヘルプを表示します")
@is_admin_channel()
async def zmhelp(interaction: discord.Interaction):
    help_text = """
**運営コマンド一覧**

`/zmst` - 鉱山の営業状況を表示・変更します
`/zmrank` - ランキング情報を表示します
`/zmadd <amount> <user>` - 指定したユーザーにジルコンを付与します
`/zmmsg <message>` - 採掘チャンネルにメッセージを投稿します
`/zmannounce` - 採掘アナウンスを手動で送信します
`/zmreset <mining/all>` - データベースをリセットします
`/zmtime [hours] [minutes]` - 採掘時間を設定します
`/zmhelp` - このヘルプを表示します

**注意事項**
- すべてのコマンドは管理チャンネルでのみ使用可能です
- データベースのリセットは慎重に行ってください
- 採掘時間の設定は24時間形式で指定してください
"""
    await interaction.response.send_message(help_text, ephemeral=True)

# Bot起動時に呼び出される関数
@client.event
async def on_ready():
    try:
        # db作成
        await mining.create_db()
        await users.create_db()
        # 定時アナウンス開始
        check_announce.start()
        # スラッシュコマンドの同期
        await tree.sync()
        # バックアップスケジューラ開始
        schedule_backup.start()
        print("Ready!")
    except Exception as e:
        print(f"起動エラー: {e}")


# 毎日0時を検知して採掘アナウンスを発火
@tasks.loop(seconds=60, reconnect=True)
async def check_announce():
    try:
        now = datetime.now(const.JST)
        # 鉱山オープンフラグがFalseならアナウンスが流れない
        if not config.MINE_OPEN:
            return
        if (now.hour in config.ANN_HOUR) and (now.minute in config.ANN_MINUTE):
            await mining.undo_done_flag()
            await send_announce()
    except Exception as e:
        print(f"アナウンスチェックエラー: {e}")


# 採掘アナウンスを送信
async def send_announce():
    try:
        # キャラクターとメッセージをランダム取得
        character = get_random_character()
        char_id = character["id"]
        char_name = character["name"]
        img_path = f"assets_character/{char_id}.png"
        img_file = discord.File(fp=img_path, filename=f"{char_id}.png")
        embed = discord.Embed(description=character["messages"])
        embed.set_author(name=char_name, icon_url=f"attachment://{char_id}.png")
        embed.set_thumbnail(url=f"attachment://{char_id}.png")
        
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
        await channel.send(embed=embed, view=view, file=img_file)
    except Exception as e:
        print(f"アナウンス送信エラー: {e}")


### 国未所属チェックはDiscordチャンネル側で設定


# ジルコン採掘アクション
async def mining_zircon(interaction: discord.Interaction):
    try:
        if not config.MINE_OPEN:
            await interaction.response.send_message(
                content=SysMsg.MINE_CLOSED, ephemeral=True
            )
            return
        country = util.get_country(interaction.user)
        # DBのレコードを見て採掘済みかチェック
        ures = await mining.get_user_single(interaction.user.id, country["role"])
        if ures is not None:
            if bool(ures[6]):  # ures[6]=done_flag
                await interaction.response.send_message(
                    content=SysMsg.ONCE_MINING, ephemeral=True
                )
                return
        # 採掘ガチャ
        result = util.gacha(random.random(), config.PROBABILITY)
        # 採掘結果がエクセレントかどうか判定
        isExcellent = result["id"] == 0
        # 採掘結果をDBに保存して、メッセージを送信
        await mining.upsert(interaction.user.id, country["role"], result["zirnum"], isExcellent)
        await users.upsert(interaction.user.id, result["zirnum"], isExcellent)

        await interaction.response.defer(thinking=True, ephemeral=True)

        # ガチャ演出のランダム化 random_performance_key, performance_num
        rpk = random.randint(1,100)
        pn_gif = int(rpk % 4)
        # ガチャ演出の表示
        fn_gif=f"mining{pn_gif}.gif"
        gif_mining = discord.File(
            fp=f"./assets/{fn_gif}",
            filename=fn_gif
        )
        em1 = make_embed.mining_performance(interaction.user, fn_gif)
        mining_msg = await interaction.followup.send(embed=em1, file=gif_mining, ephemeral=True)
        await asyncio.sleep(3)

        pn_img = int(rpk % (result["id"] + 3))
        fn_img = f"{result['msg']}{pn_img}.png"
        img_mresult = discord.File(
            fp=f"{config.CWD}/assets/{fn_img}",
            filename=fn_img,
        )
        ures = await mining.get_user_single(interaction.user.id, country["role"])
        em2 = make_embed.mining(result, interaction.user, ures[3], fn_img)
        await mining_msg.delete()
        await interaction.followup.send(embed=em2, file=img_mresult, ephemeral=True)
        # 採掘結果が「Excellent!!」の場合、各国雑談チャンネルに投稿する
        if isExcellent:
            exc_embed = make_embed.excellent(interaction.user)
            channel = client.get_channel(country["chid"])
            img_ex = discord.File(
                fp=f"{config.CWD}/assets/{const.EX_CELEB}",
                filename=f"{const.EX_CELEB}",
            )
            await channel.send(file=img_ex, embed=exc_embed)
    except Exception as e:
        print(f"採掘処理エラー: {e}")
        await interaction.response.send_message(
            content="採掘処理中にエラーが発生しました。", ephemeral=True
        )


# 自身の統計量（採掘数、採掘回数、Ex数、自身のRank）を表示するアクション
async def get_stats_self(interaction: discord.Interaction):
    try:
        country = util.get_country(interaction.user)
        # 基本採掘情報を取得
        result_mining = await mining.get_user_single(interaction.user.id, country["role"])
        result_lifetime = await users.get_single(interaction.user.id)
        if result_lifetime is None:
            await interaction.response.send_message(SysMsg.DATA_NOT_FOUND, ephemeral=True)
            return
        elif result_mining is None:
            result_mining = [int(interaction.user.id), country["id"], 0, 0, 0, 0, 0]
        
        # 自分のランクを取得
        rank_list = await mining.get_rank_user_country(country["role"])
        rank_self = 0
        for r in rank_list:
            if r[1] == interaction.user.id:  # r[1]はuserid
                rank_self = r[0]  # r[0]はrank
                break
                
        # embed作成して返信
        embed = make_embed.stats_self(
            result_mining, result_lifetime, interaction.user, rank_self
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"統計表示エラー: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                content="統計情報の取得中にエラーが発生しました。",
                ephemeral=True
            )


# 所属国の統計量（採掘数、採掘回数、ランキングTop10）を表示するアクション
async def get_stats_country(interaction: discord.Interaction):
    try:
        country = util.get_country(interaction.user)
        # 国統計データを取得
        result_country = await mining.get_country_single(country["role"])
        if result_country is None:
            result_country = (country["role"], 0, 0)

        # ランク情報の取得
        result_rank = await mining.get_rank_user_country(country["role"])
        # 自分の順位を取得
        rank_self = 0
        for r in result_rank:
            if r[1] == interaction.user.id:  # r[1]はuserid
                rank_self = r[0]  # r[0]はrank
                break
                
        # TOP10を取得
        formatted_rank = []
        for r in result_rank[:10]:  # 上位10件のみ取得
            user = interaction.guild.get_member(r[1])  # r[1]はuserid
            formatted_rank.append([
                r[0],  # rank
                user.display_name if user is not None else "None",  # ユーザー名
                r[2]  # zirnum（採掘量）
            ])

        flag_of_country = discord.File(
            fp=f"{config.CWD}/assets/{country['name']}.jpg",
            filename=f"{country['name']}.jpg",
        )
        embed = make_embed.stats_country(
            result_country, country["name"], formatted_rank, rank_self
        )
        await interaction.response.send_message(
            file=flag_of_country, embed=embed, ephemeral=True
        )
    except Exception as e:
        print(f"国統計表示エラー: {e}")
        await interaction.response.send_message(
            content="国統計情報の取得中にエラーが発生しました。", ephemeral=True
        )


### 以下は運営コマンド

def mine_status(isMineOpen):
    return "OPEN" if config.MINE_OPEN else "CLOSE"

# ボタンIDと処理関数のマッピング
BUTTON_HANDLERS = {
    cids.MINING_ZIRCON: mining_zircon,
    cids.COUNTRY_STATS: get_stats_country,
    cids.SELF_STATS: get_stats_self
}

# mine_status で「営業状況：OPEN/CLOSE [OPEN][CLOSE]」→「OPEN/CLOSEしますか？ [YES][NO]」→「OPEN/CLOSEしました」となるUIを作る（優先度：中）
# 全イベントの監視
@client.event
async def on_interaction(interaction: discord.Interaction):
    try:
        if hasattr(interaction, 'data') and 'component_type' in interaction.data:
            if interaction.data["component_type"] == 2:  # Button
                custom_id = interaction.data["custom_id"]
                if custom_id in BUTTON_HANDLERS:
                    await BUTTON_HANDLERS[custom_id](interaction)
    except Exception as e:
        print(f"ボタン処理エラー: {e}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    content="ボタン処理中にエラーが発生しました。",
                    ephemeral=True
                )
        except Exception:
            pass  # 既に応答済みの場合は無視

# バックアップスケジューラ
@tasks.loop(hours=24)
async def schedule_backup():
    """24時間ごとにバックアップを実行する（鉱山がOPENの場合のみ）"""
    try:
        # 鉱山がOPENの場合のみバックアップを実行
        if config.MINE_OPEN:
            backup_files = perform_backup()
            print(f"バックアップが完了しました: {backup_files}")
        else:
            print("鉱山がCLOSEのため、バックアップをスキップしました")
    except Exception as e:
        print(f"バックアップ中にエラーが発生しました: {e}")

# Bot起動
client.run(config.DISCORD_TOKEN)
