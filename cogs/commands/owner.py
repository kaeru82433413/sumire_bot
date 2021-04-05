from discord.ext import commands
import discord


class Owner(commands.Cog, name="owner"):
  """
  bot所有者用コマンド
  """
  def __init__(self, bot):
    self.bot = bot
  
  async def cog_check(self, ctx):
    if await self.bot.is_owner(ctx.author):
      return True
    else:
      raise commands.NotOwner

  @commands.command(aliases=["db", "sql"])
  async def database(self, ctx, *, sentence):
    """
    DBにクエリを送ります
    <query>
    """
    res = self.bot.postgres(sentence)
    if res is None:
      await ctx.message.add_reaction("\N{White Heavy Check Mark}")
    else:
      await ctx.send(res)
  
  @commands.command(name="error")
  async def error_cmd(self, ctx, error_name, *, arg):
    """
    指定した例外を発生させます
    <error>
    """
    error_name = error_name.lower()
    for error in filter(lambda x: x.__name__.lower() == error_name, [Exception] + Exception.__subclasses__()):
      raise error(arg)
    else:
      await ctx.send("一致する例外がありませんでした")
  
def setup(bot):
  bot.add_cog(Owner(bot))