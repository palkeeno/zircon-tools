import discord
from utils.helpers import get_country
from models import mining, users
import config.config as config
from config.role_manager import RoleProbabilityManager
from consts import sysmsg as SysMsg
from services.embeds import stats_self, stats_country


async def get_stats_self(interaction: discord.Interaction):
    """自身の統計量表示アクション"""
    try:
        country = get_country(interaction.user)
        roleid = country["role"] if country is not None else 0
        # 基本採掘情報を取得
        result_mining = await mining.get_user_single(interaction.user.id, roleid)
        result_lifetime = await users.get_single(interaction.user.id)
        if result_lifetime is None:
            await interaction.response.send_message(SysMsg.DATA_NOT_FOUND, ephemeral=True)
            return
        elif result_mining is None:
            result_mining = [int(interaction.user.id), country["id"] if country else 0, 0, 0, 0, 0, 0]
        # 自分のランクを取得（国ロール保持者のみ）
        rank_self = 0
        if country is not None:
            rank_list = await mining.get_rank_user_country(country["role"])
            for r in rank_list:
                if r[1] == interaction.user.id:
                    rank_self = r[0]
                    break
        
        # 適用ロールを取得
        role_manager = RoleProbabilityManager()
        applicable_role = role_manager.get_applicable_role(interaction.user)
                
        # embed作成して返信
        embed = stats_self(
            result_mining, result_lifetime, interaction.user, rank_self
        )
        
        # 適用ロールがある場合は表示
        if applicable_role:
            embed.add_field(
                name="適用ロール",
                value=f"🎭 {applicable_role['role_name']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"統計表示エラー: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                content="統計情報の取得中にエラーが発生しました。",
                ephemeral=True
            )


async def get_stats_country(interaction: discord.Interaction):
    """所属国の統計量（採掘数、採掘回数、ランキングTop10）を表示するアクション"""
    try:
        country = get_country(interaction.user)
        if country is None:
            await interaction.response.send_message(
                content="国ロール未保持者は国サマリを表示できません。", ephemeral=True
            )
            return
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
        embed = stats_country(
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
