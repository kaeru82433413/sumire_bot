from discord.ext import commands
import discord
from operator import itemgetter
import random
import re
from datetime import datetime, timedelta

def _point_transition(nickname, before=None, after=None, increase=None):
    if sum(map(lambda x: x is None, [before, after, increase])) != 1:
        raise ValueError("キーワード引数を2つ指定してください")
    
    if after is None:
        after = before + increase
    elif before is None:
        before = after - increase
    
    return f"{nickname}の所持ポイント：{before}→{after}"

class SumireServer(commands.Cog, name="sumire"):
    """
    すみれちゃんの遊戯室 用のコマンド
    """
    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx):
        return isinstance(ctx.channel, discord.DMChannel) or ctx.guild == self.bot.sumire_server
    
    @commands.group(name="point", aliases=["pt"], invoke_without_command=True)
    async def point_cmd(self, ctx):
        """
        pointに関するコマンドです
        """
        await ctx.send_help(ctx.command)
    
    @point_cmd.command(name="check")
    async def point_check(self, ctx, member: discord.Member=None):
        """
        対象メンバーのポイントを表示します
        memberが指定されていない場合は実行者が対象になります
        botを指定することはできません
        [member]
        """
        
        if member is None:
            member = ctx.author

        if member.bot:
            await ctx.send("botを指定しないでください！")
            return

        nickname, point = ctx.bot.member_data(member, ("nickname", "point"))
        await ctx.send(f"{nickname}の所持ポイントは{point}ptです")
    
    @point_cmd.command()
    async def daily(self, ctx):
        """
        ランダムでポイントが手に入ります
        1日に1回のみ使用可能、日付の境目は午前4時(JST)です
        []
        """
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        if now.hour < 4:
            yesterday = today - timedelta(days=1)
            last_border = yesterday + timedelta(seconds=60*60*4)
        else:
            last_border = today + timedelta(seconds=60*60*4)
        
        before_point, last_daily, nickname = self.bot.member_data(ctx.author, ("point", "last_daily", "nickname"))

        if last_daily <= last_border:
            increase = random.randint(8, 16)
            self.bot.postgres("update members set point = point + %s, last_daily = %s where id = %s", increase, now, ctx.author.id)
            await ctx.send(f"デイリーボーナスを受け取りました！{increase}ptゲット！\n{_point_transition(nickname, before=before_point, increase=increase)}")

        else:
            await ctx.send("今日の分は既に受け取っています")
    
    @point_cmd.command(name="random")
    async def point_random(self, ctx, value: int):
        """
        ランダムでポイントを増減させます
        50%で指定数増え、残りの50%で指定数減ります
        valueは自然数で指定してください。また、所持ポイントより大きい値は指定できません
        <value>
        """

        if value <= 0:
            await ctx.send(f"{value}は自然数ではありませんよ？")
            return
        
        before_point, name = ctx.bot.member_data(ctx.author, ("point", "nickname"))
        if before_point < value:
            await ctx.send(f"所持ポイントが足りないため実行できません(所持ポイント:{before_point})")
            return

        result = random.randrange(-1, 2, 2)
        ctx.bot.postgres("update members set point = point + %s where id = %s", value*result, ctx.author.id)
        
        message = {-1: "残念！はずれ！", 1: "おめでとう！あたり！"}[result]
        await ctx.send(f"{message}\n{_point_transition(name, before=before_point, increase=value*result)}")


    @point_cmd.command(aliases=["giveaway"])
    async def transfer(self, ctx, target: discord.Member, point: int):
        """
        自分のポイントを他人に譲渡します
        pointは自然数で指定してください。また、所持ポイントより大きい値は指定できません
        botを指定することはできません
        <target> <point>
        """
        
        if point <= 0:
            await ctx.send(f"{point}は自然数ではありませんよ？")
            return
        
        if target.bot:
            await ctx.send("botを指定しないでください！")
            return

        
        author_point, author_name = ctx.bot.member_data(ctx.author, ("point", "nickname"))
        if author_point < point:
            await ctx.send(f"所持ポイントが足りないため実行できません(所持ポイント:{author_point})")
            return
        
        target_point, target_name = ctx.bot.member_data(target, ("point", "nickname"))

        ctx.bot.postgres("update members set point = point - %s where id = %s", point, ctx.author.id)
        ctx.bot.postgres("update members set point = point + %s where id = %s", point, target.id)
        await ctx.send(f"{target_name}に{point}ポイント譲渡しました\n{_point_transition(author_name, before=author_point, increase=-point)}\n{_point_transition(target_name, before=target_point, increase=point)}")
        



    @point_cmd.command()
    async def ranking(self, ctx, page=1):
        """
        メンバーのポイントランキングを表示します
        デフォルトで上位20人、ページを指定すると20*page-19から20*page位までを取得します
        ページ数は自然数で指定してください
        [page]
        """
        if page <= 0:
            await ctx.send(f"{page}は自然数ではありませんよ？")
            return

        members = [member for member in self.bot.sumire_server.members if not member.bot]
        res = ctx.bot.members_data(members, ("id", "point", "nickname"))

        res = sorted(res, key=itemgetter(1), reverse=True)
        target_members = res[page*20-20:page*20]
        if not target_members:
            await ctx.send(f"{page}ページ目は存在しません")
            return
        
        ranking_embed = discord.Embed(title=f"ポイントランキング ({page}/{(len(res)-1)//20+1}ページ)")
        ranking_rows = [f"{i}位 {point}pt: {name}" for i, (_, point, name) in enumerate(target_members, 20*(page-1)+1)]
        ranking_embed.description = "\n".join(ranking_rows)
        await ctx.send(embed=ranking_embed)
    
    @commands.group(name="nickname", aliases=["nick"], invoke_without_command=True)
    async def nickname_cmd(self, ctx):
        """
        botに保存されているニックネームの確認・変更を行います
        このニックネームが設定されていると、botのメッセージに名前が表示される際にユーザー名やサーバーのニックネームの代わりに表示されます
        """
        await ctx.send_help(ctx.command)
    
    @nickname_cmd.command(name="check")
    async def nickname_check(self, ctx, member: discord.Member=None):
        """
        対象のメンバーのニックネームを表示します
        memberが指定されていない場合は実行者が対象になります
        [member]
        """
        if member is None:
            member = ctx.author
        nickname, = ctx.bot.member_data(member, ("nickname",), True)
        if nickname is None:
            await ctx.send(f"{member}のニックネームは未設定です")
        else:
            await ctx.send(f"{member}のニックネームは{repr(nickname)}に設定されています")
    
    @nickname_cmd.command(name="set")
    async def nickname_set(self, ctx, nickname=None):
        """
        実行者ニックネームを設定します
        ニックネームが指定されていない場合は未設定状態にします
        左右の空白文字は無視されます
        ニックネームは1~32文字で指定してください
        他人のニックネームの変更はできません
        ~~やりたければ「お兄ちゃん」とか「ご主人様」とか「豚野郎」とかでもどうぞ。ただしふざけすぎには注意~~
        [nickname]
        """

        if nickname is not None:
            nickname = nickname.strip()
            if not 1 <= len(nickname) <= 32:
                await ctx.send("ニックネームは1~32文字で指定してください")
                return
            if "\n" in nickname:
                await ctx.send("ニックネームに改行文字を含むことはできません")
                return

        old_nickname, = ctx.bot.member_data(ctx.author, ("nickname",), True)

        if nickname == old_nickname:
            if nickname is not None:
                await ctx.send(f"ニックネームは既に{repr(nickname)}に設定されています")
            else:
                await ctx.send(f"ニックネームは既に未設定です")
            return

        ctx.bot.postgres("update members set nickname = %s where id = %s", nickname, ctx.author.id)
        if old_nickname is None:
            await ctx.send(f"ニックネームを{repr(nickname)}に設定しました")
        elif nickname is None:
            await ctx.send(f"ニックネームを{repr(old_nickname)}から未設定にしました")
        else:
            await ctx.send(f"ニックネームを{repr(old_nickname)}から{repr(nickname)}に変更しました")
    
    
def setup(bot):
    bot.add_cog(SumireServer(bot))
