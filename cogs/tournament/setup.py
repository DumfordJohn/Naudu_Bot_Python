import discord
from discord.ext import commands
from tournament_data import load_tournaments, save_tournaments

class TournamentSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments = load_tournaments()

    ADMIN_ROLE_NAME = "admin"

    def is_admin():
        async def predicate(ctx):
            role_names = [role.name for role in ctx.author.roles]
            return TournamentSetup.ADMIN_ROLE_NAME in role_names
        return commands.check(predicate)

    @commands.command()
    @is_admin()
    async def create_tournament(self, ctx, name: str, tournament_type: str):
        if name in self.tournaments:
            await ctx.send(f"Tournament `{name}` already exists.")
            return

        if tournament_type.lower() not in ["single", "double", "roundrobin"]:
            await ctx.send("Invalid tournament type. Choose from: single, double, roundrobin.")
            return

        signup_channel = discord.utils.get(self.bot.get_all_channels(), name="sign-ups")
        if signup_channel is None:
            await ctx.send("Could not find a #sign-ups channel.")
            return

        embed = discord.Embed(
            title=f"Tournament sign-up: {name}",
            description="React with ✅ to join!",
            color=discord.Color.green()
        )
        embed.add_field(name="Players", value="No signups yet!", inline=False)

        signup_msg = await signup_channel.send(embed=embed)
        await signup_msg.add_reaction("✅")

        self.tournaments[name] = {
            "type": tournament_type.lower(),
            "players": [],
            "message_id": signup_msg.id,
            "channel_id": signup_channel.id
        }

        save_tournaments(self.tournaments)
        await ctx.send(f"✅ Tournament `{name}` created! Sign-ups are open in {signup_channel.mention}.")

async def setup(bot):
    await bot.add_cog(TournamentSetup(bot))
