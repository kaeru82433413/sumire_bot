from discord.ext import commands
import discord
import os
from datetime import datetime
import asyncio
import traceback
import io

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready.")
        print(f"{self.bot.user.id}")
        if os.name == "posix": # Herokuで起動されていれば
            login_notice_ch = self.bot.get_channel(769174714538786847)
            await login_notice_ch.send(f"{self.bot.user} がログインしたよ！")
        
        if not hasattr(self.bot, "sumire_server"):
            self.bot.__class__.sumire_server = self.bot.get_guild(504299765379366912)
        if not hasattr(self.bot, "error_report_channel"):
            type(self.bot).error_report_channel = self.bot.get_channel(782423473569660969)

        now = datetime.now()
        wait_time = 60 - (now.second + now.microsecond*10**-6)
        await asyncio.sleep(wait_time)
        self.bot.cogs["Loops"].minutely.start() # 00秒ちょうどにループを開始
    
    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild

        mentioned = False
        if self.bot.user in message.mentions: # ユーザーにメンションされたらTrue
            mentioned = True
        else:
            if isinstance(guild, discord.Guild):
                if set(guild.get_member(self.bot.user.id).roles) & set(message.role_mentions):    # 役職にメンションされたらTrue
                    mentioned = True
        if mentioned:
            tenshi_hat_emoji = self.bot.get_emoji(845899764645756998)
            await message.add_reaction(tenshi_hat_emoji)

        if isinstance(message.channel, discord.DMChannel):
            if message.author.id not in (self.bot.user.id, 481027469202423808): # bot自身, かえるさん#0785 のメッセージは除く
                dm_ch = self.bot.get_channel(771654931941425163)
                
                embed = discord.Embed(description=message.content, timestamp=message.created_at)
                icon = message.author.avatar_url_as()
                embed.set_author(name=message.author.name, icon_url=icon)
                await dm_ch.send(embed=embed)

                if message.attachments:
                    files = await self.bot.attachments_to_files(message)
                    await dm_ch.send(files=files)
                


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.suggest_command(ctx)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send("引数を解析できませんでした")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("引数が足りないみたいですよ！")
        elif isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
            await ctx.send("おかしな引数が渡されたみたい…")
        elif isinstance(error, (commands.MissingPermissions, commands.NotOwner)):
            await ctx.send("あなたがこのコマンドを使うなんて127年早い！")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("ここでは使えません")
        else:

            error = getattr(error, "original", error)
            error_tb = traceback.TracebackException.from_exception(error)

            report_embed = discord.Embed(title="Error", color=0xffff00 if ctx.bot.local else 0xff0000, timestamp=ctx.message.created_at)
            if hasattr(ctx.guild, "name"):
                report_embed.add_field(name="Guild", value=ctx.guild.name)
            if hasattr(ctx.channel, "name"):
                report_embed.add_field(name="Channel", value=ctx.channel.name)
            report_embed.add_field(name="Author", value=ctx.author.name)
            report_embed.add_field(name="Content", value=ctx.message.content)
            report_embed.add_field(name="MessageURL", value=ctx.message.jump_url)
            
            tb_format = "".join(error_tb.format())
            if len(tb_format) <= 1000:
                report_embed.add_field(name="Traceback", value="```"+tb_format+"```", inline=False)
            traceback_file = discord.File(io.BytesIO(tb_format.encode()), filename="traceback.txt")

            await ctx.bot.error_report_channel.send(embed=report_embed, file=traceback_file)

            error_embed = discord.Embed(title="エラーが発生しました")
            error_embed.description = discord.utils.escape_markdown("".join(error_tb.format_exception_only())) + "開発者に報告しました。修正をお待ちください"
            await ctx.send(embed=error_embed)
    

    async def suggest_command(self, ctx):
        candidates = []

        for command in self.bot.walk_commands():
            if ctx.invoked_with in {command.name, *command.aliases}:
                candidates.append(command)
        
        if not candidates:
            return
        
        suggest_embed = discord.Embed(title=f"{ctx.invoked_with}というコマンドはありません", description="もしかしたら以下のコマンドかも？")
        
        for command in candidates:
            command_query = [command.name]
            parent = command
            while (parent := parent.parent) is not None:
                command_query.append(parent.name)
            command_query.reverse()

            suggest_embed.add_field(name=ctx.prefix+" ".join(command_query), value=command.short_doc)

        await ctx.send(embed=suggest_embed)

def setup(bot):
    bot.add_cog(Events(bot))
