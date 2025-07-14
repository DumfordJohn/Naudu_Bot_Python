import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=None, intents=intents)

@bot.event
async def on_ready():
    if not hasattr(bot, "synced"):
        await bot.tree.sync()
        bot.synced = True
        print("Synced global commands:")
        for command in await bot.tree.fetch_commands():
            print(f" - /{command.name}: {command.description}")
    print(f"Logged in as {bot.user}")

async def load_all_cogs():
    for root, _, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("_") and filename != "match_view.py":
                module = os.path.join(root, filename)[:-3].replace(os.sep, ".")
                try:
                    await bot.load_extension(module)
                    print(f"Loaded cog: {module}")
                except Exception as e:
                    print(f"Failed to load cog: {module}: {e}")

async def main():
    async with bot:
        await load_all_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())