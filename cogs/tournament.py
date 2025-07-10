import json
import os
import discord
from discord.ext import commands

TOURNAMENT_FILE = "tournaments.json"

def load_tournaments():
    if not os.path.exists(TOURNAMENT_FILE):
        return {}
    with open(TOURNAMENT_FILE, "r") as f:
        return json.load(f)

def save_tournaments(tournaments):
    with open(TOURNAMENT_FILE, "w") as f:
        json.dump(tournaments, f, indent=4)

class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments = load_tournaments()
    
    ADMIN_ROLE_NAME = "admin"
    
    def is_admin():
        async def predicate(ctx):
            role_names = [role.name for role in ctx.author.roles]
            return Tournament.ADMIN_ROLE_NAME in role_names
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

        self.tournaments[name] = {
            "type": tournament_type.lower(),
            "players": [],
            "message_id": None
        }

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

        await ctx.send(f"✅ Tournamet `{name}` created! Sign-ups are open in {signup_channel.mention}")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        for name, tournament in self.tournaments.items():
            if tournament.get("message_id") == payload.message_id and str(payload.emoji) == "✅":
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)

                if member and all(p['id'] != member.id for p in tournament["players"]):
                    tournament["players"].append({
                        "name": member.display_name,
                        "id": member.id
                    })
                    save_tournaments(self.tournaments)

                    channel = guild.get_channel(tournament["channel_id"])
                    message = await channel.fetch_message(tournament["message_id"])
                    embed = message.embeds[0]

                    player_names = [p['name'] for p in tournament["players"]]
                    players_text = "\n".join(player_names) if player_names else "No sign-ups yet!"
                    new_embed = discord.Embed(
                        title=embed.title,
                        description=embed.description,
                        color=embed.color
                    )
                    new_embed.add_field(
                        name="Players",
                        value=players_text,
                        inline=False
                    )
                    await message.edit(embed=new_embed)


async def setup(bot):
    await bot.add_cog(Tournament(bot))