from discord.ext import commands
import discord
from cogs.help_command import SumireBotHelp
import os
from traceback import TracebackException
from operator import attrgetter, itemgetter
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def dynamic_prefix(bot, message):
  if os.name=="nt": # ローカル起動時のデバッグ用
    return ("?",)

  prefixes = ["s/", "!"]
  if "コマンド" in getattr(message.channel, "name", ""):
    prefixes.append("")
  return prefixes


class SumireBot(commands.Bot):
  sumire_server = None
  def __init__(self):
    intents = discord.Intents.all()
    super().__init__(command_prefix=dynamic_prefix, intents=intents, help_command=SumireBotHelp())
    cogs = ["cogs.commands.general", "cogs.commands.sumire_server", "cogs.commands.seichi", "cogs.commands.test", "cogs.commands.admin", "cogs.commands.owner",
            "cogs.events", "cogs.loops", "jishaku"]
    for cog in cogs:
      self.load_extension(cog)
  
  def run(self):
    TOKEN = os.getenv("sumire_bot_token")
    super().run(TOKEN)
  
  @staticmethod
  def postgres(sentence, *params):
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
  
  def get_nickname(self, member, name):
    if name is not None:
      return name
    else:
      if isinstance(member, discord.User):
        member = self.sumire_server.get_member(member.id)
      return member.display_name

  def member_data(self, member, raw_name=False):
    res = self.postgres("select * from members where id = %s", member.id)
    if not res:
      self.postgres("insert into members (id) values (%s)", member.id)
      res = (member.id, 100, None)
    else:
      res = res[0]

    if raw_name:
      return res
    return res[:2] + (self.get_nickname(member, res[2]),)

  def members_data(self, members, raw_name=False):
    member_ids = tuple(map(attrgetter("id"), members))
    res = self.postgres("select * from members where id in %s", member_ids)
    membeds_dict = {member.id: member for member in members}

    for member_id in set(member_ids) - set(map(itemgetter(0), res)):
      self.postgres("insert into members (id) values (%s)", member_id)
      res.append((member_id, 100, None))

    if raw_name:
      return res
    res = [(member_id, point, self.get_nickname(membeds_dict[member_id], nickname)) for member_id, point, nickname in res]
    return res

if __name__ == "__main__":
  bot = SumireBot()
  bot.run()
