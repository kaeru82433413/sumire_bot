from discord.ext import commands
import discord
from cogs.help_command import SumireBotHelp
import os
import sys
import datetime
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
    if bot.local: # ローカル起動時のデバッグ用
        return "?"

    prefixes = ["s/", "!"]
    if "コマンド" in getattr(message.channel, "name", ""):
        prefixes.append("")
    return prefixes


class SumireBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=dynamic_prefix, intents=intents, help_command=SumireBotHelp())
        cogs = ["cogs.commands.general", "cogs.commands.sumire_server", "cogs.commands.seichi", "cogs.commands.test",
                        "cogs.commands.admin", "cogs.commands.owner",
                        "cogs.events", "cogs.loops", "cogs.anti_spam", "jishaku"]
        for cog in cogs:
            self.load_extension(cog)
        self.local = os.name=="nt"
    
    def run(self):
        TOKEN = os.getenv("sumire_bot_token")
        super().run(TOKEN)
    
    async def on_error(self, *args, **kwargs):
        now_utc = datetime.datetime.now() - datetime.timedelta(hours=9)
        report_embed = discord.Embed(title="Error", color=0xffff00 if self.local else 0xff0000, timestamp=now_utc)

        report_embed.add_field(name="Event", value=args[0])
        if len(args) > 1:
            report_embed.add_field(name="Args", value=args[1:])
        if kwargs:
            report_embed.add_field(name="KwArgs", value=kwargs)

        if "error" in kwargs:
            error = kwargs.pop("error")
        else:
            error = sys.exc_info()[1]
        tb_format = self.exception_format(error)
        if len(tb_format) <= 1000:
            report_embed.add_field(name="Traceback", value="```"+tb_format+"```", inline=False)
        traceback_file = discord.File(io.BytesIO(tb_format.encode()), filename="traceback.txt")

        await self.error_report_channel.send(embed=report_embed, file=traceback_file)


    def postgres(self, sql, *params, error_as_str=False):
        try:
            cur.execute(sql, params)
        except psycopg2.ProgrammingError as e:
            if error_as_str:
                return self.exception_format(e)
            raise e

        try:
            return cur.fetchall()
        except psycopg2.ProgrammingError as e:
            return None # 結果がなければNoneを返す
    

    @staticmethod
    def point_transition(nickname, before=None, after=None, increase=None):
        if [before, after, increase].count(None) != 1:
            raise ValueError("キーワード引数を2つ指定してください")
        
        if after is None:
            after = before + increase
        elif before is None:
            before = after - increase
        
        return f"{nickname}の所持ポイント：{before}→{after}"
    

    @staticmethod
    def exception_format(exception: Exception):
        tb = TracebackException.from_exception(exception)
        return "".join(tb.format_exception_only())
    

    @staticmethod
    async def attachments_to_files(message):
        files = []
        for attachment in message.attachments:
            file_data = io.BytesIO(await attachment.read())
            filename, spoiler = attachment.filename, attachment.is_spoiler()
            file = discord.File(file_data, filename, spoiler=spoiler)
            files.append(file)
        return files


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
