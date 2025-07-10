import discord
import random
from discord.ext import commands
from tournament_data import load_tournaments, save_tournaments
from .match_view import MatchView

class TournamentStart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments = load_tournaments()

    @commands.command()
    async def start_tournament(self, ctx, name: str):
        if name not in self.tournaments:
            await ctx.send(f"Touranment `{name}` does not exist.")
            return

        tournament = self.tournaments[name]
        players = tournament.get("players", [])

        if len(players) < 2:
            await ctx.send("Not enough players to start a tournament.")
            return

        random.shuffle(players)
        matchups = []

        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                matchups.append((players[i]["name"], players[i + 1]["name"]))
            else:
                matchups.append((players[i]["name"], "BYE"))

        channel = self.bot.get_channel(tournament["channel_id"])
        signup_message = await channel.fetch_message(tournament["message_id"])

        thread = await signup_message.create_thread(
            name=f"{name} Bracket",
            auto_archive_duration=60,
            reason="Tournament start"
        )

        for i, (p1, p2) in enumerate(matchups):
            embed = discord.Embed(
                title=f"Match {i+1}: {p1} vs {p2}",
                descritption="Click a button below to report the winner.",
                color=discord.Color.green()
            )
            view = MatchView(
                tournament_name=name,
                match_index=i,
                player1=p1,
                player2=p2
            )

        await thread.send(embed=embed, view=view)

        tournament["matches"] = matchups
        save_tournaments()

        await ctx.send(f"Tournament `{name}` has started! Check the thread: {thread.mention}")

async def setup(bot):
    await bot.add_cog(TournamentStart(bot))