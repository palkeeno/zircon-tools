import asyncio
import random
import discord
from utils.helpers import get_country, gacha
from models import mining, users
import config.config as config
from config.role_manager import RoleProbabilityManager
from consts import sysmsg as SysMsg
from consts import const
from services.embeds import mining_performance, mining as mining_embed, excellent


async def mining_zircon(interaction: discord.Interaction, client):
    """ジルコン採掘アクション"""
    try:
        if not config.get_mine_open():
            await interaction.response.send_message(
                content=SysMsg.MINE_CLOSED, ephemeral=True
            )
            return
        country = get_country(interaction.user)
        if country is None:
            await interaction.response.send_message(
                content="国選択をした方のみ参加できます！", ephemeral=True
            )
            return
        # DBのレコードを見て採掘済みかチェック
        ures = await mining.get_user_single(interaction.user.id, country["role"])
        if ures is not None:
            if bool(ures[6]):  # ures[6]=done_flag
                await interaction.response.send_message(
                    content=SysMsg.get_once_mining_message(), ephemeral=True
                )
                return
        
        # ロール別確率を取得
        role_manager = RoleProbabilityManager()
        user_probability = role_manager.get_user_probability(interaction.user, config.get_probability())
        
        # 採掘ガチャ
        result = gacha(random.random(), user_probability)
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
        em1 = mining_performance(interaction.user, fn_gif)
        mining_msg = await interaction.followup.send(embed=em1, file=gif_mining, ephemeral=True)
        await asyncio.sleep(3)

        pn_img = int(rpk % (result["id"] + 3))
        fn_img = f"{result['msg']}{pn_img}.png"
        img_mresult = discord.File(
            fp=f"{config.CWD}/assets/{fn_img}",
            filename=fn_img,
        )
        total = (ures[3] if ures is not None else 0) + result["zirnum"]
        em2 = mining_embed(result, interaction.user, total, fn_img)
        await mining_msg.delete()
        await interaction.followup.send(embed=em2, file=img_mresult, ephemeral=True)
        # 採掘結果が「Excellent!!」の場合、各国雑談チャンネルに投稿する
        if isExcellent:
            exc_embed = excellent(interaction.user)
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
