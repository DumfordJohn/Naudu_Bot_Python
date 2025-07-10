import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

GUILD_ID = 1125407155537854504

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=None, intents=intents)

@bot.event
async def on_ready():
    if not hasattr(bot, "synced"):
        guild = discord.Object(id=GUILD_ID)  # 👈 your guild ID here
        await bot.tree.sync(guild=guild)
        bot.synced = True
    print(f"✅ Logged in as {bot.user}")

    # 🔍 List commands registered in the guild
    guild = discord.Object(id=GUILD_ID)
    commands = await bot.tree.fetch_commands(guild=guild)
    print(f"📋 Commands in guild {GUILD_ID}:")
    for cmd in commands:
        print(f"- /{cmd.name}: {cmd.description}")


async def load_all_cogs():
    for root, dirs, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("_") and filename != "match_view.py":
                filepath = os.path.join(root, filename)
                module = filepath[:-3].replace("/", ".").replace("\\", ".")
                try:
                    await bot.load_extension(module)
                    print(f"✅ Loaded cog: {module}")
                except Exception as e:
                    print(f"❌ Failed to load {module}: {e}")

async def main():
    async with bot:
        await load_all_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
