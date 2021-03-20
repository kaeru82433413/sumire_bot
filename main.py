from discord.ext import commands
import discord
import os
from traceback import TracebackException
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def dynamic_prefix(bot, message):
  prefixes = ["s/", "!"]
  if "コマンド" in getattr(message.channel, "name", ""):
    prefixes.append("")
  return prefixes

class SumireBot(commands.Bot):
  def __init__(self):
    intents = discord.Intents.all()
    super().__init__(command_prefix=dynamic_prefix, intents=intents)
    for cog in ("cogs.commands", "cogs.events", "cogs.loops", "jishaku"):
      self.load_extension(cog)
  
  def run(self):
    TOKEN = os.getenv("sumire_bot_token")
    super().run(TOKEN)
  

  @staticmethod
  def postgres(sentence, params=()):
    with psycopg2.connect(DATABASE_URL) as conn:
      with conn.cursor() as cur:
        try:
          cur.execute(sentence, params)
        except psycopg2.ProgrammingError as e:
          tb = TracebackException.from_exception(e)
          return "".join(tb.format_exception_only())

        try:
          return list(cur)
        except psycopg2.ProgrammingError as e:
          return None

  @classmethod
  def member_data(cls, member: discord.Member):
    res = cls.postgres("select * from members where id = %s", (member.id,))
    if not res:
      cls.postgres("insert into members (id) values (%s)", (member.id,))
      return (member.id, 0, None)
    else:
      return res

if __name__ == "__main__":
  bot = SumireBot()
  bot.run()
