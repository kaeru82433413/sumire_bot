from discord.ext import commands
import discord
import io

class Test(commands.Cog, name="test"):
  """
  botの仕様確認用コマンド
  """
  def __init__(self, bot):
    self.bot = bot
    
  @commands.command(name="arg")
  async def arg_cmd(self, ctx, arg):
    """
    引数を1つだけ受け取り、表示します
    <*arg*>
    """
    await ctx.send(repr(arg))
  
  @commands.command(name="args")
  async def args_cmd(self, ctx, *args):
    """
    引数を複数受け取り、表示します
    [*args*…]
    """
    await ctx.send(args)
  

  @commands.group(invoke_without_command=True)
  async def converter(self, ctx):
    """
    converterの動作確認用
    """
    await ctx.send_help(ctx.command)

def setup(bot):
  bot.add_cog(Test(bot))