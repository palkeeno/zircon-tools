import discord
import csv
import io
from datetime import datetime
import models.mining as mining
import models.users as users

async def get_rank_countries(interaction: discord.Interaction):
    try:
        # 国別採掘量を取得
        countries = await mining.get_country_ranks()
        
        # 埋め込みメッセージを作成
        embed = discord.Embed(
            title="国別採掘量ランキング",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # ランキングを追加
        for i, (country, amount) in enumerate(countries, 1):
            embed.add_field(
                name=f"{i}位: {country}",
                value=f"{amount:,} :gem:",
                inline=False
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"ランキング表示エラー: {e}")
        await interaction.response.send_message(
            "ランキングの表示中にエラーが発生しました",
            ephemeral=True
        )

async def output_event_stats_csv(interaction: discord.Interaction):
    try:
        # イベント統計（現在の採掘イベント）を取得
        stats = await mining.get_all_event_stats(interaction.guild)
        
        # CSVファイルを作成
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["順位", "ユーザ名", "メンションID", "国名", "採掘量", "採掘回数", "Excellent回数"])
        
        for i, stat in enumerate(stats, 1):
            writer.writerow([
                i,
                stat["username"],
                stat["mention"],
                stat["country"],
                stat["zirnum"],
                stat["m_cnt"],
                stat["ex_cnt"]
            ])
            
        # ファイルを添付して送信
        file = discord.File(
            io.BytesIO(output.getvalue().encode()),
            filename=f"event_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        await interaction.response.send_message(
            "イベント統計CSVを生成しました",
            file=file,
            ephemeral=True
        )
    except Exception as e:
        print(f"イベント統計CSV出力エラー: {e}")
        await interaction.response.send_message(
            "CSVの生成中にエラーが発生しました",
            ephemeral=True
        )

async def output_lifetime_stats_csv(interaction: discord.Interaction):
    try:
        # 累積統計（生涯合計）を取得
        stats = await users.get_all_lifetime_stats(interaction.guild)
        
        # CSVファイルを作成
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["順位", "ユーザ名", "メンションID", "国名", "採掘量", "採掘回数", "Excellent回数"])
        
        for i, stat in enumerate(stats, 1):
            writer.writerow([
                i,
                stat["username"],
                stat["mention"],
                stat["country"],
                stat["lt_total"],
                stat["m_cnt"],
                stat["ex_cnt"]
            ])
            
        # ファイルを添付して送信
        file = discord.File(
            io.BytesIO(output.getvalue().encode()),
            filename=f"lifetime_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        await interaction.response.send_message(
            "累積統計CSVを生成しました",
            file=file,
            ephemeral=True
        )
    except Exception as e:
        print(f"累積統計CSV出力エラー: {e}")
        await interaction.response.send_message(
            "CSVの生成中にエラーが発生しました",
            ephemeral=True
        )

class RankView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="国採掘量ランク", style=discord.ButtonStyle.primary)
    async def country_rank(self, interaction: discord.Interaction, button: discord.ui.Button):
        await get_rank_countries(interaction)
        
    @discord.ui.button(label="イベント統計出力", style=discord.ButtonStyle.secondary)
    async def event_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await output_event_stats_csv(interaction)
        
    @discord.ui.button(label="累積統計出力", style=discord.ButtonStyle.secondary)
    async def lifetime_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await output_lifetime_stats_csv(interaction) 