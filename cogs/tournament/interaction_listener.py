import discord
from discord.ext import commands
from tournament_data import load_tournaments, save_tournaments

class InteractionListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id", "")
        if "|" not in custom_id:
            return

        try:
            tournament_name, match_index_str, winner_index_str = custom_id.split("|")
            match_index = int(match_index_str)
            winner_index = int(winner_index_str)
        except ValueError:
            await interaction.response.send_message("Invalid button format.", ephemeral=True)
            return

        tournaments = load_tournaments()
        tournament = tournaments.get(tournament_name)

        if not tournament or match_index >= len(tournament.get("matches", [])):
            await interaction.response.send_message("❌ Match not found.", ephemeral=True)
            return

        match = tournament["matches"][match_index]
        winner = match[winner_index - 1]

        await interaction.response.send_message(f"🏆 **{winner}** has been marked as the winner of match {match_index + 1}!", ephemeral=False)

        # You can now store the winner in the tournament JSON if you want
        # e.g., tournament["results"] = {match_index: winner}
        # Then save:
        save_tournaments(tournaments)

async def setup(bot):
    await bot.add_cog(InteractionListener(bot))
