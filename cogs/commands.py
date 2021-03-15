from discord.ext import commands
import discord


class Commands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  @commands.has_permissions(administrator=True)
  async def remove(self, ctx, limit: int=1):
    async for message in ctx.history(limit=limit+1):
      try:
        await message.delete()
      except discord.NotFound:
        break
  
  @commands.command(aliases=["db", "sql"])
  @commands.is_owner()
  async def database(self, ctx, sentence):
    pass

def setup(bot):
  bot.add_cog(Commands(bot))