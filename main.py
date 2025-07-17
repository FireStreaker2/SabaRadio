import util.config
import util.embeds
import discord
from discord.ext import commands
from os import listdir

bot = commands.Bot(intents=discord.Intents.default())

for filename in listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name="Saba"),
    )

    await bot.sync_commands()


@bot.event
async def on_command_error(ctx, error):
    return await ctx.respond(
        embed=util.embeds.error_embed(error),
        ephemeral=True,
    )


bot.run(util.config.TOKEN)
