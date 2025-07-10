# cogs/tournament/signup_add.py

import discord
from discord.ext import commands
from tournament_data import load_tournaments, save_tournaments

class SignupAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return  # Ignore the bot’s own reaction

        if str(payload.emoji) != "🎮":
            return  # Only trigger on 🎮

        tournaments = load_tournaments()

        for name, tournament in tournaments.items():
            if payload.message_id == tournament.get("message_id"):
                # Found the right tournament
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                if not member:
                    return

                player_entry = {"name": member.display_name, "id": member.id}

                if any(p["id"] == member.id for p in tournament["players"]):
                    return  # Already signed up

                tournament["players"].append(player_entry)
                save_tournaments(tournaments)

                # Update the embed
                channel = guild.get_channel(tournament["channel_id"])
                message = await channel.fetch_message(tournament["message_id"])
                embed = message.embeds[0]
                names = "\n".join([p["name"] for p in tournament["players"]])
                embed.description = f"React with 🎮 to join!\n\n**Players Signed Up:**\n{names}"
                await message.edit(embed=embed)

                break

async def setup(bot):
    await bot.add_cog(SignupAdd(bot))
