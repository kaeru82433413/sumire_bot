from discord.ext import commands
import discord
from typing import Union


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
    

    @commands.command()
    async def send(self, ctx, target: Union[discord.TextChannel, discord.DMChannel, discord.User, discord.Member], *, content=""):
        """
        targetにcontentの内容を送信します
        attachmentsが存在する場合は添付します
        <target> [content]
        """
        
        content = content.strip()
        if not ctx.message.attachments:

            if not content:
                await ctx.send("contentが空です")
                return
            await target.send(content)

        else:
            await target.send(content, files=await ctx.bot.attachments_to_files(ctx.message))
    

    @commands.command(name="error")
    async def error_cmd(self, ctx, error_name="Exception", *, arg=None):
        """
        指定した例外を発生させます
        <error>
        """
        error_name = error_name.lower()
        for error in filter(lambda x: x.__name__.lower() == error_name, [Exception] + Exception.__subclasses__()):
            if arg is None:
                raise error
            else:
                raise error(arg)
        else:
            await ctx.send("一致する例外がありませんでした")
    
def setup(bot):
    bot.add_cog(Owner(bot))