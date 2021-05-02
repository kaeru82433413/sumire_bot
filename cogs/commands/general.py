from discord.ext import commands
import discord
import os
import math
import calc
from calc import expression

class General(commands.Cog, name="general"):
    """
    一般的なコマンド
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def info(self, ctx, function):
        """
        botの各機能の詳細を表示します
        未実装
        [function]
        """
        pass
    
    @commands.command(name="calc")
    async def calculator(self, ctx, *, text):
        """
        数式を計算します
        数値の整数部分にはカンマを含めることができます。例：82,433,413
        数値指数表記ができます。例：3.402823e+38
        +-*/の四則演算に加えて、^のべき乗が使えます。例：2^31-1
        数値の各記号の間には任意の空白文字を挿入しても構いません。例：( 40 - 20 ) * 10
        abs, floor, ceil, sin, cos, tan, radian, degreeの8つの関数が使えます
        例：sin(radian(45))
        tick, sec, min, hour, day, st, c, lc, chunk, unit, star, k, m, g, %, pi, radian, degreeの18個の単位が使えます。直前の値を定数倍します
        使用例：1day/30min
        <expression>
        """
        text = text.replace(r"\*", "*")
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
        各コマンドの引数にはcalcコマンドと同様の数式が使用できますが、引数を複数受け取るコマンドは空白文字で区切られます
        """
        await ctx.send_help(ctx.command)
    
    @math_cmd.command(aliases=["pf", "primefactorization"])
    async def prime_factorization(self, ctx, *, value: expression("natural")):
        """
        素因数分解を行います
        2以上を整数を指定してください
        <value>
        """
        if value < 2:
            raise commands.BadArgument
        
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

    @math_cmd.command()
    async def gcd(self, ctx, *values: expression("natural")):
        """
        引数の最大公約数を求めます
        引数は自然数でなくてはいけません
        [values…]
        """
        await ctx.send(math.gcd(*values))

    @math_cmd.command()
    async def lcm(self, ctx, *values: expression("natural")):
        """
        引数の最小公倍数を求めます
        引数は自然数でなくてはいけません
        [values…]
        """
        await ctx.send(math.lcm(*values))


def setup(bot):
    bot.add_cog(General(bot))