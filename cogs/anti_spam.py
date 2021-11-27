import asyncio
import discord
from discord.ext import commands
from collections import defaultdict, deque
from datetime import timedelta

from discord.ext.commands.core import check

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_log = defaultdict(deque)
        self.confirming = {} # {user: reason}
    

    @commands.Cog.listener()
    async def on_ready(self):
        self.system_notification_channel = self.bot.get_channel(914066346810179614)
    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in (self.bot.user.id, self.bot.owner_id):
            return
        if message.guild == self.bot.sumire_server:
            await self.in_sumire_server(message)


    async def in_sumire_server(self, message):
        user = message.author
        if user in self.confirming:
            await self.ban(user)
            return
        
        user_messages = self.message_log[user]
        user_messages.append(message)
        while len(user_messages) > 10:
            # 過剰な記録を削除
            user_messages.popleft()
        
        if len(message.mentions+message.role_mentions) >= 3:
            await self.spam_confirm(message, f"1メッセージにメンションが{len(message.mentions+message.role_mentions)}個含まれていたため")

        """elif message.channel.id != 838603446990405683: # botコマンド連投用 は除く
            if len(user_messages) >= 5 and self.check_time(user_messages[-5], message, 10):
                await self.spam_confirm(message, "10秒間に5メッセージ送信したため")
            elif len(user_messages) >= 2 and user_messages[-2].content == message.content and self.check_time(user_messages[-2], message, 60):
                await self.spam_confirm(message, "同一内容のメッセージを送信したため")"""
    

    async def spam_confirm(self, message, reason=None):
        user = message.author
        self.confirming[user] = reason
        dm_ch = (await user.send("あなたはスパム疑惑を受けました\n現在、すみれちゃんの遊戯室で発言するとBANされます。このチャンネルで発言することで、この状態を解除することができます。60秒以内に返答がない場合BANします")).channel
        try:
            await self.bot.wait_for("message", check=lambda m: (m.channel, m.author) == (dm_ch, user), timeout=60)
        except asyncio.TimeoutError:
            if user not in message.guild.members:
                # 既に退出済みなら
                return
            await self.ban(user)
            return
        if user not in message.guild.members:
            return
        self.confirming.pop(user)
        await dm_ch.send("受理しました\nもう発言しても大丈夫ですよ!")
        self.message_log[user].clear()
    

    async def ban(self, user):
        reason = self.confirming[user]
        await user.ban(reason=reason)
        notification_contents = [f"{user}をスパム対策機構によりBANしました。"]
        if reason is not None:
            notification_contents.append(reason)
        await self.system_notification_channel.send("\n".join(notification_contents))

    

    @staticmethod
    def check_time(first, second, seconds):
        """
        firstが送信されてからsecondが送信されるまでの時間がseconds以下か
        """
        return second.created_at - first.created_at <= timedelta(seconds=seconds)


def setup(bot):
    bot.add_cog(AntiSpam(bot))