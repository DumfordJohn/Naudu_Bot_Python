import discord
from discord.ext import commands
from tournament_data import load_tournaments, save_tournaments

class TournamentInteractionListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data or "custom_id" not in interaction.data:
            return

        custom_id = interaction.data["custom_id"]
        if "|" not in custom_id:
            return

        try:
            tournament_name, match_index, winner_index = custom_id.split("|")
            match_index = int(match_index)
            winner_index = int(winner_index)
        except Exception:
            await interaction.response.send_message("Invalid button data.", emphemeral=True)
            return

        tournaments = load_tournaments()
        tournament = tournaments.get(tournament_name)

        if not tournament:
            await interaction.response.send_message("Tournament not found.", emphemeral=True)
            return

        match = tournament["matches"][match_index]
        winner = match[winner_index - 1]
        match_result = f"WINNER **{winner}**"

        tournament["matches"][match_index] = {
            "players": match,
            "winner": winner
        }
        save_tournaments()

        embed = discord.Embed(
            title=f"Match {match_index + 1}: {match[0]} vs {match[1]}",
            description=match_result,
            color=discord.Color.blue()
        )

        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message(f"Winner recorded: {winner}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TournamentInteractionListener(bot))