import discord
from discord.ext import commands, tasks
from datetime import datetime
import seichi

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

  async def daily(self, now):
    date = now.month, now.day
    if date in seichi.ACHIEVEMENTS:
      ach_id, ach_name = seichi.ACHIEVEMENTS[date]
      regular_notice_ch = self.bot.get_channel(820939592999108648)
      embed = discord.Embed(title="整地鯖の記念日実績が解除できます", color=0x00ffff)
      embed.description = f"本日は 「{ach_name}」です\n実績No{ach_id}を解除していない人は忘れずに解除しましょう"
      await regular_notice_ch.send(embed=embed)


def setup(bot):
  bot.add_cog(Loops(bot))