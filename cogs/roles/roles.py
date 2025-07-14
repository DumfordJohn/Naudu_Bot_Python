import discord
import json
import os
from discord.ext import commands
from discord import app_commands

CONFIG_DIR = "reaction_configs"
os.makedirs(CONFIG_DIR, exist_ok=True)

def config_path(guild: discord.Guild):
    safe_name = guild.name.replace(" ", "_").replace("/", "_")
    return os.path.join(CONFIG_DIR, f"{safe_name}.json")

def load_config(guild: discord.Guild):
    path = config_path(guild)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_config(guild: discord.Guild, config):
    path = config_path(guild)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_ids = {}

    @app_commands.command(name="setup_roles", description="Configure the reaction roles")
    async def setup_roles(self, interaction: discord.Interaction):
        save_config(interaction.guild, {})
        await interaction.response.send_message("Use `/add_roles` to map emojis, then `/post_roles` to send the embed.", ephemeral=True)

    @app_commands.command(name="add_roles", description="Add an emoji-role pair to config")
    @app_commands.describe(emoji="The emoji to use", role="The role to assign")
    async def add_roles(self, interaction: discord.Interaction, emoji: str, role: discord.Role):
        config = load_config(interaction.guild)
        config[emoji] = role.name
        save_config(interaction.guild, config)
        await interaction.response.send_message(f"Mapped {emoji} to role '{role.name}'", ephemeral=True)

    @app_commands.command(name="edit_roles", description="Edit the emoji-role pairs in config.")
    @app_commands.describe(emoji="This is the emoji to update", new_role="The new role to assign")
    async def edit_roles(self, interaction: discord.Interaction, emoji: str, new_role: discord.Role):
        config = load_config(interaction.guild)
        if emoji not in config:
            await interaction.response.send_message(f"{emoji} is not configured.", ephemeral=True)
            return

        config[emoji] = new_role.name
        save_config(interaction.guild, config)
        await interaction.response.send_message(f"Updated {emoji} to new role `{new_role.name}`", ephemeral=True)

    @app_commands.command(name="post_roles", description="Post the reaction roles embed")
    async def post_roles(self, interaction: discord.Interaction):
        config = load_config(interaction.guild)
        if not config:
            await interaction.response.send_message("No emoji-role mappings found. Use `/add_roles` first.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Choose your Roles!",
            description="\n".join(f"{emoji} - {role}" for emoji, role in config.items()),
            color=discord.Color.green()
        )

        msg = await interaction.channel.send(embed=embed)
        self.message_ids[interaction.guild.id] = msg.id

        for emoji in config:
            await msg.add_reaction(emoji)

        await interaction.response.send_message("Reaction role message posted", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print(f"Reaction added: emoji={payload.emoji}, user_id={payload.user_id}, message_id={payload.message_id}")

        if payload.user_id == self.bot.user.id:
            return

        if self.message_ids.get(payload.guild_id) != payload.message_id:
            print(f"⛔ Message ID does not match configured message for guild {payload.guild_id}")
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji)
        config = load_config(guild)

        print(f"🔍 Looking up config for guild_id={payload.guild_id}")
        role_name = config.get(emoji)

        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                print(f"✅ Role match found. Trying to assign role '{role.name}' to user '{member.display_name}'")
                try:
                    await member.add_roles(role)
                    print(f"🎉 Role '{role.name}' added to {member.display_name}")
                except discord.Forbidden:
                    print(f"⚠️ Missing permissions to add role '{role.name}'")
                except discord.HTTPException as e:
                    print(f"❌ Failed to add role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if self.message_ids.get(payload.guild_id) != payload.message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji)
        config = load_config(guild)
        role_name = config.get(emoji)

        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.remove_roles(role)
                print(f"Role '{role.name}' removed from {member.display_name}.")

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))