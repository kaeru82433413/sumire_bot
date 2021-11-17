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
    async def database(self, ctx, *, query):
        """
        DBにクエリを送ります
        <query>
        """
        res = self.bot.postgres(query, error_as_str=True)
        if res is None:
            await ctx.message.add_reaction("\N{White Heavy Check Mark}")
        elif isinstance(res, str):
            await ctx.send(f"```{res}```")
        else:
            await ctx.send(res)
    

    @commands.group(aliases=["ptm"], invoke_without_command=True)
    async def pt_manage(self, ctx):
        """
        ポイントの管理をします
        """
        await ctx.send_help(ctx.command)


    @pt_manage.command(name="set")
    async def ptm_set(self, ctx, value: int, target: discord.Member=None):
        """
        対象のポイントを指定した値に変更します
        <value> [target]
        """
        if target is None:
            target = ctx.bot.sumire_server.get_member(ctx.author.id)
            if target is None:
                raise commands.BadArgument
        
        if target.guild != ctx.bot.sumire_server:
            await ctx.send(f"{ctx.bot.sumire_server.name}のメンバーを指定してください")
            return
        
        before_point, = ctx.bot.member_data(target.id, ("point",))
        ctx.bot.postgres("update members set point = %s where id = %s", value, target.id)
        await ctx.send(ctx.bot.point_transition(target.display_name, before=before_point, after=value))
    

    @pt_manage.command(name="add")
    async def ptm_add(self, ctx, value: int, target: discord.Member=None):
        """
        対象のポイントに指定した値を加算します
        <value> [target]
        """
        if target is None:
            target = ctx.bot.sumire_server.get_member(ctx.author.id)
            if target is None:
                raise commands.BadArgument
        
        if target.guild != ctx.bot.sumire_server:
            await ctx.send(f"{ctx.bot.sumire_server.name}のメンバーを指定してください")
            return
        
        before_point, = ctx.bot.member_data(target.id, ("point",))
        ctx.bot.postgres("update members set point += %s where id = %s", value, target.id)
        await ctx.send(ctx.bot.point_transition(target.display_name, before=before_point, increase=value))
    

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