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

async def output_rank_csv(interaction: discord.Interaction):
    try:
        # ユーザー統計を取得
        stats = await users.get_all_stats()
        
        # CSVファイルを作成
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ユーザーID", "国", "総採掘量", "最終採掘日時"])
        
        for stat in stats:
            writer.writerow([
                stat["user_id"],
                stat["country"],
                stat["total_amount"],
                stat["last_mined"]
            ])
            
        # ファイルを添付して送信
        file = discord.File(
            io.BytesIO(output.getvalue().encode()),
            filename=f"user_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        await interaction.response.send_message(
            "ユーザー統計CSVを生成しました",
            file=file,
            ephemeral=True
        )
    except Exception as e:
        print(f"CSV出力エラー: {e}")
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
        
    @discord.ui.button(label="ユーザ統計CSV", style=discord.ButtonStyle.secondary)
    async def user_csv(self, interaction: discord.Interaction, button: discord.ui.Button):
        await output_rank_csv(interaction) 