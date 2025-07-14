import json
import discord
import aiohttp
import asyncio
from discord.ext import commands, tasks
from discord import app_commands
import os
from bot import GUILD_ID


TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
CONFIG_FILE = "cogs/twitch_ping/twitch_ping_config.json"

class TwitchNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.access_token = None
        self.headers = {}
        self.config = self.load_config()
        self.check_stream.start()

    def cog_unload(self):
        self.check_stream.cancel()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)

    async def get_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, params=params) as resp:
                data = await resp.json()
                self.access_token = data["access_token"]
                self.headers = {
                    "Client-ID": TWITCH_CLIENT_ID,
                    "Authorization": f"Bearer {self.access_token}",
                }

    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="set_ping", description="Set the streamer and Discord channel to notify")
    @app_commands.describe(streamer="Twitch streamer username", channel="Channel to post the notifications")
    async def set_ping(self, interaction: discord.Interaction, streamer: str, channel: discord.TextChannel):
        self.config[str(interaction.guild_id)] = {
            "streamer": streamer,
            "channel_id": channel.id
        }
        self.save_config()
        await interaction.response.send_message(f"Notifications set for '{streamer}' in '{channel.mention}'", ephemeral=True)

    @tasks.loop(minutes=1)
    async def check_stream(self):
        if not self.access_token:
            await self.get_token()

        for guild_id, settings in self.config.items():
            streamer_login = settings["streamer"]
            channel_id = settings["channel_id"]

            url = f"https://api.twitch.tv/helix/streams?user_login={streamer_login}"
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if data.get("data"):
                        stream = data["data"][0]
                        title = stream["title"]
                        game = stream.get("game_name", "")
                        thumbnail = stream["thumbnail_url"].replace("{width}", "1280").replace("{height}", "720")

                        embed = discord.Embed(
                            title=title,
                            url=f"https://twitch.tv/{streamer_login}",
                            description=f"{streamer_login} is now live playing {game}!",
                            color=discord.Color.blue()
                        )
                        embed.set_image(url=thumbnail)
                        embed.set_author(name=streamer_login, url=f"https://twitch.tv/{streamer_login}", icon_url="https://static-cdn.jtvnw.net/jtv_user_pictures/hosted_images/TwitchGlitchPurple.png")

                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            await channel.send(f"{streamer_login} is live!", embed=embed)

async def setup(bot):
    await bot.add_cog(TwitchNotifier(bot))