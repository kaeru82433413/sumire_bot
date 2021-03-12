from discord.ext import commands
import discord

def bot_owner(ctx):
  return ctx.bot.is_owner(ctx.author)

class Commands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  @commands.has_permissions(administrator=True)
  async def remove(self, ctx, limit: int=1):
    async for message in ctx.history(limit=limit+1):
      await message.delete()
  
  @commands.command()
  @commands.check(bot_owner)
  async def db(self, ctx, sentence):
    pass

def setup(bot):
  bot.add_cog(Commands(bot))