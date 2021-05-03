from discord.ext import commands
import discord
import io

class Test(commands.Cog, name="test"):
    """
    botの仕様確認用コマンド
    基本的に開発用ですが、自由に使ってもらって構いません
    """
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="arg")
    async def arg_cmd(self, ctx, arg):
        """
        引数を1つだけ受け取り、表示します
        <arg>
        """
        await ctx.send(repr(arg))
    
    @commands.command(name="args")
    async def args_cmd(self, ctx, *args):
        """
        引数を複数受け取り、表示します
        [args…]
        """
        await ctx.send(args)
    
    @commands.command(name="kwarg")
    async def kwarg_cmd(self, ctx, *, kwarg):
        """
        キーワード引数を受け取り、表示します
        空白で区切っても1つの引数と解釈します
        <kwarg>
        """
        await ctx.send(repr(kwarg))

    @commands.command(name="raw_kwarg", aliases=["rkwarg"], rest_is_raw=True)
    async def raw_kwarg_cmd(self, ctx, *, kwarg):
        """
        キーワード引数を受け取り、コマンド名の直後の空白文字も含めた結果を表示します
        空白で区切っても1つの引数と解釈します
        <kwarg>
        """
        await ctx.send(repr(kwarg))


    @commands.group(invoke_without_command=True)
    async def converter(self, ctx):
        """
        converterの動作確認用
        <arg>
        """
        await ctx.send_help(ctx.command)
    
    @converter.command(name="member")
    async def conveter_member(self, ctx, member: discord.Member):
        """
        メンバーを取得します
        <member>
        """
        await ctx.send(member)

def setup(bot):
    bot.add_cog(Test(bot))