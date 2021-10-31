import discord
from discord.ext import commands, tasks
from datetime import datetime, date
from operator import attrgetter
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
        if now.hour == 0:
            await self.daily(now)
        if now.hour == 22:
            await self.daily22h(now)

    async def daily(self, now):
        today_achievements = seichi_data.get_today_achievements(now)
        if today_achievements:
            regular_notice_ch = self.bot.get_channel(820939592999108648)
            seichi_acv_ntc_role = self.bot.sumire_server.get_role(876675066329432114)
            embed = discord.Embed(title="整地鯖の記念日実績が解除できます", color=0xffff00)

            ach_ids, ach_names = zip(*today_achievements)
            embed.description = f"本日は 「{'」と「'.join(ach_names)}」です\n実績No{','.join(map(str, ach_ids))}を解除していない人は忘れずに解除しましょう"

            await regular_notice_ch.send(seichi_acv_ntc_role.mention, embed=embed)
        
        self.record_point(now.date())

    
    async def daily22h(self, now):
        today_achievements = seichi_data.get_today_achievements(now)
        if today_achievements:
            regular_notice_ch = self.bot.get_channel(820939592999108648)
            seichi_acv_ntc_role = self.bot.sumire_server.get_role(876675066329432114)
            embed = discord.Embed(title="整地鯖記念日実績の解除をお忘れではありませんか？", color=0xffff00)

            ach_ids, ach_names = zip(*today_achievements)
            embed.description = f"本日は 「{'」と「'.join(ach_names)}」です\n年に一度の機会なので、解除し忘れないようにしましょう"

            await regular_notice_ch.send(seichi_acv_ntc_role.mention, embed=embed)
    

    def record_point(self, today: date):
        members = {member.id: member for member in self.bot.sumire_server.members if not member.bot}
        members_data = self.bot.members_data(map(attrgetter("id"), members.values()), ("id", "point"))
        for id_, point in members_data:
            member = members[id_]
            self.bot.postgres("insert into point_record (id, point, display_name, date) values (%s, %s, %s, %s);",
                               id_, point, member.display_name, today)

    
    @minutely.error
    async def minutely_error(self, error):
        await self.bot.on_error("minutely" ,error=error)


def setup(bot):
    bot.add_cog(Loops(bot))