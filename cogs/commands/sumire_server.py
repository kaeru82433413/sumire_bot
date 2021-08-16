from discord.ext import commands
import discord
from operator import itemgetter, attrgetter
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
    ROLES = {
        876675066329432114: "<#820939592999108648>で整地鯖の記念日実績を通知します"
    }
    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx):
        return ctx.guild == self.bot.sumire_server
    
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

        point, = ctx.bot.member_data(member.id, ("point",))
        await ctx.send(f"{member.display_name}の所持ポイントは{point}ptです")
    
    @point_cmd.command()
    async def daily(self, ctx):
        """
        ランダムでポイントが手に入ります
        1日に1回のみ使用可能、日付の境目は午前4時(JST)です
        []
        """
        now = datetime.now()
        today = datetime(now.year, now.month, now.day) # 0時00分に変換
        if now.hour < 4: # 4時より前なら、前日の4時が境目
            yesterday = today - timedelta(days=1)
            last_border = yesterday + timedelta(seconds=60*60*4)
        else: # そうでなければ、当日の4時が境目
            last_border = today + timedelta(seconds=60*60*4)
        
        before_point, last_daily = self.bot.member_data(ctx.author.id, ("point", "last_daily"))

        if last_daily < last_border: # 最後に受け取ったのが境目より前なら
            increase = random.randint(8, 16)
            self.bot.postgres("update members set point = point + %s, last_daily = %s where id = %s", increase, now, ctx.author.id)
            await ctx.send(f"デイリーボーナスを受け取りました！{increase}ptゲット！\n{_point_transition(ctx.author.display_name, before=before_point, increase=increase)}")

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
        
        before_point, = ctx.bot.member_data(ctx.author.id, ("point",))
        if before_point < value:
            await ctx.send(f"所持ポイントが足りないため実行できません(所持ポイント:{before_point})")
            return

        result = random.randrange(-1, 2, 2)
        ctx.bot.postgres("update members set point = point + %s where id = %s", value*result, ctx.author.id)
        
        message = {-1: "残念！はずれ！", 1: "おめでとう！あたり！"}[result]
        await ctx.send(f"{message}\n{_point_transition(ctx.author.display_name, before=before_point, increase=value*result)}")


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

        
        author_point, = ctx.bot.member_data(ctx.author.id, ("point",))
        if author_point < point:
            await ctx.send(f"所持ポイントが足りないため実行できません(所持ポイント:{author_point})")
            return
        
        target_point, = ctx.bot.member_data(target.id, ("point",))

        ctx.bot.postgres("update members set point = point - %s where id = %s", point, ctx.author.id)
        ctx.bot.postgres("update members set point = point + %s where id = %s", point, target.id)
        await ctx.send(
            f"{target.display_name}に{point}ポイント譲渡しました\n"
            f"{_point_transition(ctx.author.display_name, before=author_point, increase=-point)}\n"
            f"{_point_transition(target.display_name, before=target_point, increase=point)}"
        )


    @point_cmd.command()
    async def ranking(self, ctx, page=1):
        """
        メンバーのポイントランキングを表示します
        デフォルトで上位10人、ページを指定すると10*page-9から10*page位までを取得します
        ページ数は自然数で指定してください
        [page]
        """
        if page <= 0:
            await ctx.send(f"{page}は自然数ではありませんよ？")
            return

        members = {member.id: member for member in self.bot.sumire_server.members if not member.bot}
        members_data = ctx.bot.members_data(map(attrgetter("id"), members.values()), ("id", "point"))

        members_data = sorted(members_data, key=itemgetter(1), reverse=True)
        max_page = (len(members_data)-1)//10 + 1 # 切り上げ除算
        if page > max_page:
            await ctx.send(f"{page}ページ目は存在しません")
            return
        
        ranking_embed = discord.Embed(title=f"ポイントランキング ({page}/{max_page}ページ)")

        ranking_rows = []
        before = (float("inf"), 0)
        for i, (member_id, point) in enumerate(members_data, 1):
            if point == before[0]: # 前の順位と同じポイントなら同じ順位にする
                i = before[1]
            else:
                before = (point, i)
            ranking_rows.append(f"{i}位 {point}pt: {members[member_id].display_name}")
        ranking_embed.description = "\n".join(ranking_rows[20*page-20:20*page])
        await ctx.send(embed=ranking_embed)
    
    @commands.group(name="role", invoke_without_command=True)
    async def role_cmd(self, ctx):
        """
        ロールの詳細表示、管理をするコマンドです
        """
        await ctx.send_help(ctx.command)


    @role_cmd.command(name="list")
    async def list_cmd(self, ctx):
        """
        着脱可能なロールの一覧を表示します
        []
        """
        roles_embed = discord.Embed(title="着脱可能なロールの一覧")
        for role_id, role_info in self.ROLES.items():
            role = self.bot.sumire_server.get_role(role_id)
            roles_embed.add_field(name=role.name, value=role_info)
        await ctx.send(embed=roles_embed)


    @role_cmd.command()
    async def add(self, ctx, role: discord.Role):
        """
        実行者にロールを付与します
        <role>
        """
        if role.id not in self.ROLES:
            await ctx.send("そのロールは付与できません")
            return
        if role in ctx.author.roles:
            await ctx.send("既に付与されています")
            return
        await ctx.author.add_roles(role)
        await ctx.send(f"{role.name}を付与しました")


    @role_cmd.command()
    async def remove(self, ctx, role: discord.Role):
        """
        実行者からロールを削除します
        <role>
        """
        if role.id not in self.ROLES:
            await ctx.send("そのロールは削除できません")
            return
        if role not in ctx.author.roles:
            await ctx.send("そのロールは付与されていません")
            return
        await ctx.author.remove_roles(role)
        await ctx.send(f"{role.name}を削除しました")

def setup(bot):
    bot.add_cog(SumireServer(bot))
