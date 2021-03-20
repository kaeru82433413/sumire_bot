from discord.ext import commands
import discord
import os
import re
import requests
import bisect
import seichi
import psycopg2


class Commands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  @commands.has_permissions(administrator=True)
  async def remove(self, ctx, limit: int=1):
    async for message in ctx.history(limit=limit+1):
      try:
        await message.delete()
      except discord.NotFound:
        break
  
  @commands.command(aliases=["sr"])
  async def seichiranking(self, ctx, player, *types):
    if not re.fullmatch(r"\w{3,16}", player):
      await ctx.send("mcidは3~16文字のアルファベット、数字、アンダーバーで指定してください")
      return
    
    mojang_res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}")
    if not mojang_res.text:
      await ctx.send("存在しないプレイヤーです")
      return
    uuid = mojang_res.json()["id"]
    uuid = "-".join([uuid[:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:]])

    types = set(types)
    TYPE_CNDS = {"break": "整地量", "build": "建築量", "playtime": "接続時間", "vote": "投票数"}
    types = [type_cnd for type_cnd in TYPE_CNDS if type_cnd in types]
    if not types: types = ["break"]

    seichi_res_json = requests.get(f"https://ranking-gigantic.seichi.click/api/ranking/player/{uuid}", params={"types":",".join(types)}).json()
    if seichi_res_json == {"message":"requested data does not exist."}:
      await ctx.send("該当データが見つかりませんでした")
      return

    embed = discord.Embed(title=f'{seichi_res_json[0]["player"]["name"]}のランキングデータ')
    for data_type, data in zip(types, seichi_res_json):
      int_data = int(data["data"]["raw_data"])

      if data_type == "break":
        if int_data >= 87115000:
          level = f"Lv200☆{int_data//87115000}"
        else:
          level = f"Lv{bisect.bisect(seichi.BREAK_LEVEL, int_data)}"
        value = f'{int_data:,} ({level})'
      
      elif data_type == "build":
        value = f'{int_data:,} (Lv{bisect.bisect(seichi.BUILD_LEVEL, int_data)})'
      
      elif data_type == "playtime":
        time_data = data["data"]["data"]
        value = f'{time_data["hours"]}時間{time_data["minutes"]}分{time_data["seconds"]}秒'
      
      elif data_type == "vote":
        value = f'{int_data:,}'

      embed.add_field(name=f'{TYPE_CNDS[data_type]} {data["rank"]}位', value=value)
    embed.set_footer(text=f'Last quit：{seichi_res_json[0]["lastquit"]}')
    await ctx.send(embed=embed)


  @commands.command(aliases=["db", "sql"])
  @commands.is_owner()
  async def database(self, ctx, sentence):
    res = self.bot.postgres(sentence)
    if res is None:
      await ctx.message.add_reaction("\N{White Heavy Check Mark}")
    else:
      await ctx.send(res)

def setup(bot):
  bot.add_cog(Commands(bot))