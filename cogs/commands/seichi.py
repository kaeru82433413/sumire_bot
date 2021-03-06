from discord.ext import commands
import discord
import re
import aiohttp
import bisect
from calc import expression
import seichi_data
from games.base import Vector

class Seichi(commands.Cog, name="seichi"):
    """
    整地鯖に関するコマンド
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["sr"])
    async def seichiranking(self, ctx, player, *types):
        """
        指定したプレイヤーの整地鯖のランキング情報を取得します
        typesはbreak, build, playtime, voteの4つが選択可能で、有効な値が渡されなかった場合はbreakを取得します
        <mcid> [types…]
        """
        if not re.fullmatch(r"\w{3,16}", player):
            await ctx.send("mcidは3~16文字のアルファベット、数字、アンダーバーで指定してください")
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{player}") as response:
                if not await response.text():
                    await ctx.send("存在しないプレイヤーです")
                    return
                uuid = (await response.json())["id"]
                uuid = "-".join([uuid[:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:]])

        types = set(types)
        TYPE_CNDS = {"break": "整地量", "build": "建築量", "playtime": "接続時間", "vote": "投票数"}
        types = [type_cnd for type_cnd in TYPE_CNDS if type_cnd in types]
        if not types: types = ["break"]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ranking-gigantic.seichi.click/api/ranking/player/{uuid}", params={"types": ",".join(types)}) as response:
                seichi_res_json = await response.json()

        if seichi_res_json == {"message":"requested data does not exist."}:
            await ctx.send("該当データが見つかりませんでした")
            return

        embed = discord.Embed(title=f'{seichi_res_json[0]["player"]["name"]}の整地鯖ランキングデータ')
        for data_type, data in zip(types, seichi_res_json):
            int_data = int(data["data"]["raw_data"])

            if data_type == "break":
                if int_data >= 87115000:
                    level = f"Lv200☆{int_data//87115000}"
                else:
                    level = f"Lv{bisect.bisect(seichi_data.BREAK_LEVEL, int_data)}"
                value = f'{int_data:,} ({level})'
            
            elif data_type == "build":
                value = f'{int_data:,} (Lv{bisect.bisect(seichi_data.BUILD_LEVEL, int_data)})'
            
            elif data_type == "playtime":
                time_data = data["data"]["data"]
                value = f'{time_data["hours"]}時間{time_data["minutes"]}分{time_data["seconds"]}秒'
            
            elif data_type == "vote":
                value = f'{int_data:,}'

            embed.add_field(name=f'{TYPE_CNDS[data_type]} {data["rank"]}位', value=value)
        embed.set_footer(text=f'Last quit：{seichi_res_json[0]["lastquit"]}')
        await ctx.send(embed=embed)
    

    @commands.command(aliases=["rgcmd"])
    async def region_cmd(self, ctx, base_x: expression("int"), base_z: expression("int"), size_x: expression("natural"), size_z: expression("natural"), direction=None):
        """
        保護のコマンドを生成します
        baseに基準となる座標、sizeに保護の大きさを指定してください。directionには(南東, 南西, 北東, 北西, SE, SW, NE, NW)のいずれかが指定できます。デフォルトは南東です。
        baseが含まれるユニットを角として、directionの方角にsize_x*size_zユニットの領域を選択するコマンドを表示します。
        baseとsizeには数式を使用できます。
        <base_x> <base_z> <size_x> <size_z> [direction]
        """

        if direction in (None, "南東", "SE"):
            direction = Vector(1, 1)
        elif direction in ("南西", "SW"):
            direction = Vector(-1, 1)
        elif direction in ("北東", "NE"):
            direction = Vector(1, -1)
        elif direction in ("北西", "NW"):
            direction = Vector(-1, -1)
        else:
            raise commands.BadArgument

        p = Vector(base_x, base_z) // 15
        q = p + (Vector(size_x, size_z)-1)*direction
        (x1, x2), (z1, z2) = map(sorted, zip(p, q))
        await ctx.send(f"//pos1 {15*x1},0,{15*z1}\n//pos2 {15*x2+14},255,{15*z2+14}")


def setup(bot):
    bot.add_cog(Seichi(bot))