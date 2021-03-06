from discord.ext import commands
import discord

class Admin(commands.Cog, name="admin"):
    """
    サーバー管理者用コマンド
    """
    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx):
        if not isinstance(ctx.author, discord.Member):
            return False
        if ctx.author.guild_permissions.administrator:
            return True
        else:
            raise commands.MissingPermissions(["administrator"])
    
    @commands.command()
    async def remove(self, ctx, limit: int=1):
        """
        使用チャンネルのメッセージを削除します
        <limit>
        """
        await ctx.channel.purge(bulk=False, limit=limit+1)

def setup(bot):
    bot.add_cog(Admin(bot))