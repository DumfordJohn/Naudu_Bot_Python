import discord
import random
from discord.ext import commands
from discord import app_commands

from bot import GUILD_ID
from tournament_data import load_tournaments, save_tournaments
from .match_view import MatchView

#GUILD_ID = 123456789012345678  # ← Replace with your server ID if you're syncing to a test server

class TournamentStart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments = load_tournaments()

    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="start_tournament", description="Start a tournament and create matches.")
    @app_commands.describe(name="The name of the tournament to start")
    async def start_tournament(self, interaction: discord.Interaction, name: str):
        print("📥 Received start_tournament command")

        # ✅ Defer immediately to prevent timeout
        await interaction.response.defer()

        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You must be an admin to start a tournament.", ephemeral=True)
            return

        if name not in self.tournaments:
            await interaction.followup.send(f"❌ Tournament `{name}` does not exist.", ephemeral=True)
            return

        tournament = self.tournaments[name]
        players = tournament.get("players", [])

        if len(players) < 2:
            await interaction.followup.send("❌ Not enough players to start the tournament.", ephemeral=True)
            return

        random.shuffle(players)
        matchups = []

        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                matchups.append((players[i]["name"], players[i + 1]["name"]))
            else:
                matchups.append((players[i]["name"], "BYE"))

        channel = interaction.channel

        try:
            signup_message = await channel.fetch_message(tournament["message_id"])
        except Exception as e:
            print(f"❌ Error fetching message: {e}")
            await interaction.followup.send("❌ Could not fetch the original signup message.", ephemeral=True)
            return

        thread = await signup_message.create_thread(
            name=f"{name} Bracket",
            auto_archive_duration=60,
            reason="Tournament start"
        )

        mentions = [f"<@{p['id']}>" for p in players]
        mention_text = " ".join(mentions)
        await thread.send(f"Tournament Starting! Participants: {mention_text}")

        for i, (p1, p2) in enumerate(matchups):
            embed = discord.Embed(
                title=f"Match {i + 1}: {p1} vs {p2}",
                description="Click a button below to report the winner.",
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
        save_tournaments(self.tournaments)

        await interaction.followup.send(f"✅ Tournament `{name}` has started! Matches posted in {thread.mention}.",
                                        ephemeral=True)


async def setup(bot):
    await bot.add_cog(TournamentStart(bot))
