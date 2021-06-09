from discord.ext import commands
import discord
from cogs.help_command import SumireBotHelp
import os
import io
from traceback import TracebackException
from operator import attrgetter, itemgetter
from typing import Union, Iterable
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

def dynamic_prefix(bot, message):
    if os.name=="nt": # ローカル起動時のデバッグ用
        return "?"

    prefixes = ["s/", "!"]
    if "コマンド" in getattr(message.channel, "name", ""):
        prefixes.append("")
    return prefixes


class SumireBot(commands.Bot):
    sumire_server = None

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=dynamic_prefix, intents=intents, help_command=SumireBotHelp())
        cogs = ["cogs.commands.general", "cogs.commands.sumire_server", "cogs.commands.seichi", "cogs.commands.test",
                        "cogs.commands.admin", "cogs.commands.owner",
                        "cogs.events", "cogs.loops", "jishaku"]
        for cog in cogs:
            self.load_extension(cog)
    
    def run(self):
        TOKEN = os.getenv("sumire_bot_token")
        super().run(TOKEN)
    
    @staticmethod
    def postgres(sql, *params):
        try:
            cur.execute(sql, params)
        except psycopg2.ProgrammingError as e:
            tb = TracebackException.from_exception(e)
            return "".join(tb.format_exception_only())

        try:
            return cur.fetchall()
        except psycopg2.ProgrammingError as e:
            return None # 結果がなければNoneを返す
    
    @staticmethod
    async def attachments_to_files(message):
        files = []
        for attachment in message.attachments:
            file_data = io.BytesIO(await attachment.read())
            filename, spoiler = attachment.filename, attachment.is_spoiler()
            file = discord.File(file_data, filename, spoiler=spoiler)
            files.append(file)
        return files

    def get_nickname(self, member, name):
        if name is not None:
            return name
        else:
            if isinstance(member, discord.User):
                member = self.sumire_server.get_member(member.id)
            return member.display_name

    def member_data(self, member_id, columns):
        res = self.postgres(f"select {', '.join(columns)} from members where id = %s", member_id)

        if not res:
            self.postgres("insert into members (id) values (%s)", member_id)
            res = self.postgres(f"select {', '.join(columns)} from members where id = %s", member_id)
        return res[0]
    

    def members_data(self, member_ids, columns):

        id_index = columns.index("id")

        member_ids = tuple(member_ids)
        res = self.postgres(f"select {', '.join(columns)} from members where id in %s", member_ids)

        for member_id in set(member_ids) - set(map(itemgetter(id_index), res)):
            res.append(self.member_data(member_id, columns))

        return res

if __name__ == "__main__":
    bot = SumireBot()
    bot.run()
