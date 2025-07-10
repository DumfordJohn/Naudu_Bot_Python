import discord
from discord.ext import commands
from tournament_data import load_tournaments, save_tournaments

class TournamentSignupAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments = load_tournaments()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        if str(payload.emoji) != "✅":
            return

        for name, tournament in self.tournaments.items():
            if tournament.get("message_id") == payload.message_id:
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                if not member:
                    member = await guild.fetch_member(payload.user_id)

                if all(p["id"] != member.id for p in tournament["players"]):
                    tournament["players"].append({"name": member.display_name, "id": member.id})
                    save_tournaments()

                    channel = guild.get_channel(tournament["channel_id"])
                    message = await channel.fetch_message(tournament["message_id"])
                    embed = message.embeds[0]

                    player_names = [p["name"] for p in tournament["players"]]
                    players_text = "\n".join(player_names) if player_names else "No signups yet!"

                    new_embed = discord.Embed(
                        title=embed.title,
                        description=embed.description,
                        color=embed.color
                    )
                    new_embed.add_field(name="Players", value=players_text, inline=False)

                    await message.edit(embed=new_embed)

async def setup(bot):
    await bot.add_cog(TournamentSignupAdd(bot))
