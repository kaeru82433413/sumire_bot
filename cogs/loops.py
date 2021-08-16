import discord
from discord.ext import commands, tasks
from datetime import datetime
import seichi_data

class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @tasks.loop(minutes=1)
    async def minutely(self):
        now = datetime.now()
        if now.minute == 0:
            await self.hourly(now)

    async def hourly(self, now):
        if now.hour == 0 or True:
            await self.daily(now)
        if now.hour == 22:
            await self.daily22h(now)

    async def daily(self, now):
        date = now.month, now.day
        if date in seichi_data.ACHIEVEMENTS:
            achievement = seichi_data.ACHIEVEMENTS[date]
            regular_notice_ch = self.bot.get_channel(820939592999108648)
            seichi_acv_ntc_role = self.bot.sumire_server.get_role(876675066329432114)
            embed = discord.Embed(title="整地鯖の記念日実績が解除できます", color=0xffff00)

            if isinstance(achievement, tuple):
                achievement = [achievement]
            ach_ids, ach_names = zip(*achievement)
            embed.description = f"本日は 「{'」と「'.join(ach_names)}」です\n実績No{','.join(map(str, ach_ids))}を解除していない人は忘れずに解除しましょう"

            await regular_notice_ch.send(seichi_acv_ntc_role.mention, embed=embed)
    
    async def daily22h(self, now):
        date = now.month, now.day
        if date in seichi_data.ACHIEVEMENTS:
            achievement = seichi_data.ACHIEVEMENTS[date]
            regular_notice_ch = self.bot.get_channel(820939592999108648)
            seichi_acv_ntc_role = self.bot.sumire_server.get_role(876675066329432114)
            embed = discord.Embed(title="整地鯖記念日実績の解除をお忘れではありませんか？", color=0xffff00)

            if isinstance(achievement, tuple):
                achievement = [achievement]
            ach_ids, ach_names = zip(*achievement)
            embed.description = f"本日は 「{'」と「'.join(ach_names)}」です\n年に一度の機会なので、解除し忘れないようにしましょう"

            await regular_notice_ch.send(seichi_acv_ntc_role.mention, embed=embed)
    
    
    @minutely.error
    async def minutely_error(self, error):
        await self.bot.on_error("minutely" ,error=error)


def setup(bot):
    bot.add_cog(Loops(bot))