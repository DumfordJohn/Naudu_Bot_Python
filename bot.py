import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def load_all_cogs():
    for root, dirs, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("_"):
                filepath = os.path.join(root, filename)
                module = filepath[:-3].replace("/", ".").replace("\\", ".")
                try:
                    await bot.load_extension(module)
                    print(f"✅ Loaded cog: {module}")
                except Exception as e:
                    print(f"❌ Failed to load {module}: {e}")


@bot.event
async def on_connect():
    await load_all_cogs()

bot.run(TOKEN)
