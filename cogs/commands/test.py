from discord.ext import commands
import discord
import io

class Test(commands.Cog, name="test"):
  """
  botの動作確認用コマンド
  """
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(name="arg")
  async def arg_cmd(self, ctx, arg):
    """
    引数を1つだけ受け取るコマンドの動作確認用
    <arg>
    """
    await ctx.send(repr(arg))
  
  @commands.command(name="args")
  async def args_cmd(self, ctx, *args):
    """
    引数を複数受け取るコマンドの動作確認用
    [args…]
    """
    await ctx.send(args)
  

def setup(bot):
  bot.add_cog(Test(bot))