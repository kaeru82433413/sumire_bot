from discord.ext import commands
import discord
import os

class SumireBot(commands.Bot):
  def __init__(self):
    intents = discord.Intents.all()
    super().__init__(command_prefix="s/", intents=intents)
    for cog in ("cogs.commands", "cogs.events", "cogs.loops", "jishaku"):
      self.load_extension(cog)
  
  def run(self):
    TOKEN = os.getenv("sumire_bot_token")
    super().run(TOKEN)
  


if __name__ == "__main__":
  bot = SumireBot()
  bot.run()
