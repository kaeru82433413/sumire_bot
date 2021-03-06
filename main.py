import os
from discord.ext import commands
import discord


if __name__ == "__main__":
  bot = commands.Bot(command_prefix="s/")
  TOKEN = os.getenv("sumirebot_token")
  bot.run(TOKEN)