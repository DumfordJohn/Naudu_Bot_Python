import discord
from discord.ext import commands
from discord import app_commands
from bot import GUILD_ID
from tournament_data import load_tournaments, save_tournaments

class TournamentSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="create_tournament", description="Create a new tournament.")
    @app_commands.describe(
        name="Name of the tournament",
        type="Tournament type (single, double, roundrobin)"
    )


    async def create_tournament(self, interaction: discord.Interaction, name: str, type: str):
        print("✅ Registered create_tournament command")
        await interaction.response.defer(ephemeral=True)
        print(f"📥 Received create_tournament: {name=} {type=}")

        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send("❌ You must be an admin to use this command.", ephemeral=True)
                return

            tournaments = load_tournaments()
            print(f"📂 Loaded tournaments: {list(tournaments.keys())}")

            if name in tournaments:
                await interaction.followup.send(f"❌ Tournament `{name}` already exists.", ephemeral=True)
                return

            if type not in ["single", "double", "roundrobin"]:
                await interaction.followup.send("❌ Invalid type. Use: `single`, `double`, or `roundrobin`.",
                                                ephemeral=True)
                return

            # 🔍 Find the sign-up channel (by name or ID)
            signup_channel = discord.utils.get(interaction.guild.text_channels, name="sign-ups")
            if not signup_channel:
                await interaction.followup.send("❌ Could not find a #sign-ups channel.", ephemeral=True)
                return

            # 📦 Create the embed
            embed = discord.Embed(
                title=f"{name} Tournament Sign-Up",
                description="React with 🎮 to join!",
                color=discord.Color.green()
            )

            print("about to send the embed")
            signup_message = await signup_channel.send(embed=embed)
            print(f"📨 Signup message sent (ID={signup_message.id})")
            await signup_message.add_reaction("🎮")


            # 💾 Save tournament info with message + channel IDs
            tournaments[name] = {
                "type": type,
                "players": [],
                "message_id": signup_message.id,
                "channel_id": signup_channel.id
            }

            save_tournaments(tournaments)
            print(f"💾 Tournament saved: {name}")

            await interaction.followup.send(
                f"✅ Tournament `{name}` created and posted in {signup_channel.mention}.",
                ephemeral=True
            )

        except Exception as e:
            print(f"[ERROR] create_tournament: {e}")
            await interaction.followup.send("❌ An unexpected error occurred.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TournamentSetup(bot))
