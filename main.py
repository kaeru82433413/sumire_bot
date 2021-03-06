from discord.ext import commands
import discord
import os

bot = commands.Bot(command_prefix="s/")

TOKEN = os.getenv("sumire_bot_token")
bot.run(TOKEN)
