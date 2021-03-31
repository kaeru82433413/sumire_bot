from discord.ext import commands
import discord
import os
import calc
from calc import expression

class General(commands.Cog, name="general"):
  """
  一般的なコマンド
  """
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(name="calc")
  async def calc_cmd(self, ctx, *text):
    """
    数式を計算します
    <expression>
    """
    text = " ".join(text).replace(r"\*", "*")
    try:
      expr = calc.Bracket(text)
    except TypeError as e:
      await ctx.send(e)
      return
    try:
      result = expr.calc()
    except ValueError as e:
      await ctx.send(e)
      return
    except ZeroDivisionError as e:
      await ctx.send("もうやめて！除算の右オペランドはとっくにゼロよ！")
      return
    await ctx.send(result)

  @commands.group(name="math", invoke_without_command=True)
  async def math_cmd(self, ctx):
    """
    様々な計算を行います
    """
    await ctx.send_help(ctx.command)
  
  @math_cmd.command(aliases=["pf", "primefactorization"])
  async def prime_factorization(self, ctx, value: expression()):
    """
    素因数分解を行います
    2以上を整数を指定してください
    <value>
    """
    if value < 2:
      await ctx.send("2以上の値を指定してください")
      return
    
    factors = []
    for i in range(2, min(value, 10**6)+1):
      exponent = 0
      while value%i == 0:
        exponent += 1
        value //= i
      if exponent > 0:
        factors.append((i, exponent))
      
      if value < i**2:
        if value > 1:
          factors.append((value, 1))
          value = 1
        break

    if value == 1:
      await ctx.send(" \* ".join(map(lambda x: f"{x[0]}^{x[1]}" if x[1]>1 else f"{x[0]}", factors)))
    else:
      await ctx.send(f"1000,000より大きな素因数を含んでいるため計算できませんでした。({value}は素数でない可能性があります)\n" + " \* ".join(map(lambda x: f"{x[0]}^{x[1]}" if x[1]>1 else f"{x[0]}", factors+[(value, 1)])))



def setup(bot):
  bot.add_cog(General(bot))