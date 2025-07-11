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
        parts = custom_id.split("|")
        if len(parts) != 4:
            return

        tournament_name, round_index, match_index, winner = parts
        round_index = int(round_index)
        match_index = int(match_index)
        winner = int(winner)

        tournaments = load_tournaments()
        tournament = tournaments.get(tournament_name)
        if not tournament:
            await interaction.response.send_message("Tournament not found.", ephemeral=True)
            return

        rounds = tournament.get("rounds", [])
        if round_index >= len(rounds) or match_index >= len(rounds[round_index]):
            await interaction.response.send_message("Match does not exist.", ephemeral=True)
            return

        match = rounds[round_index][match_index]

        if isinstance(match, (list, tuple)):
            p1, p2 = match
        elif isinstance(match, dict):
            p1 = match.get("player1")
            p2 = match.get("player2")
            if "winner" in match:
                await interaction.response.send_message("Winner already chosen for this match.", empheral=True)
                return
        else:
            await interaction.response.send_message("Invalid match data.", emphemeral=True)
            return

        winner_name = p1 if winner == 1 else p2

        rounds[round_index][match_index] = {
            "player1": p1,
            "player2": p2,
            "winner": winner_name
        }
        save_tournaments(tournaments)

        all_finished = all(isinstance(m, dict) and "winner" in m for m in rounds[round_index])

        if not all_finished:
            await interaction.response.send_message(f"Match recorded: **{winner_name} Wins!**")
            return

        winners = [m["winner"] for m in rounds[round_index]]
        if len(winners) == 1:
            await interaction.followup.send(f"Tournament **{tournament_name}** winner: **{winners[0]}**")
            return

        import random
        random.shuffle(winners)
        next_round = []
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                next_round.append((winners[i], winners[i + 1]))
            else:
                next_round.append((winners[i], "BYE"))

        new_round_index = len(rounds)
        tournament["rounds"].append(next_round)
        save_tournaments(tournaments)

        thread = interaction.channel if isinstance(interaction.channel, discord.Thread) else None
        if thread:
            from cogs.tournament.match_view import MatchView
            for i, (p1, p2) in enumerate(next_round):
                embed = discord.Embed(
                    title=f"Next Round - Match {i+1}: {p1} vs {p2}",
                    description="Click a button below to report the winner.",
                    color=discord.Color.green()
                )
                p1_id = f"<@{p1}" if p1.isdigit() else p1
                p2_id = f"<@{p2}" if p2.isdigit() else p2
                embed.add_field(name="Participants", value=f"{p1_id} vs {p2_id}", inline=False)

                view = MatchView(
                    tournament_name=tournament_name,
                    round_index=new_round_index,
                    match_index=i,
                    player1=p1,
                    player2=p2
                )
                await thread.send(embed=embed, view=view)

        await interaction.response.send_message(f"Match recorded: **{winner_name}**. Next round started!")

async def setup(bot):
    await bot.add_cog(InteractionListener(bot))