from discord.ext import commands
import discord

class SumireBotHelp(commands.HelpCommand):
  def __init__(self):
    help_doc = """
    引数なしで実行するとカテゴリの一覧を表示します
    引数にカテゴリまたはコマンドを指定すると詳細を表示します
    [*category*|*command*]
    """.strip()
    super().__init__(command_attrs={"help":help_doc})
    self.help = help_doc
  
  @staticmethod
  def parents_aliases(command):
    parents = []
    for parent in list(reversed(command.parents)) + [command]:
      if parent.aliases:
        parents.append(f'<{"|".join([parent.name] + parent.aliases)}>')
      else:
        parents.append(parent.name)
    
    return " ".join(parents)

  def command_not_found(self, string):
    return f"*{discord.utils.escape_markdown(string)}*というカテゴリまたはコマンドはありません"
  

  def subcommand_not_found(self, command, string):
    return f"{command.qualified_name}のサブコマンドに*{discord.utils.escape_markdown(string)}*というコマンドはありません"
  

  async def send_bot_help(self, mapping):
    ctx = self.context

    help_embed = discord.Embed(title="botの説明")

    category_count = 0
    for cog, commands_ in mapping.items():
      if cog is None or not commands_ or cog.qualified_name in {"admin", "owner", "Jishaku"}:
        continue
      help_embed.add_field(name=cog.qualified_name, value=cog.description, inline=False)
      category_count += 1
    
    help_embed.insert_field_at(0, name="help", value="help " + self.help.rsplit("\n", 1)[1] + "\n" + self.help.rsplit("\n", 1)[0] + f"\n一般使用できるカテゴリは以下の{category_count}つです", inline=False)
    
    command_ch = self.context.bot.get_channel(770246431796625458)
    help_embed.add_field(name="その他", value=f"prefixは「s/」と「!」が使えます。{command_ch.mention} ではprefixを省略できます", inline=False)

    await self.get_destination().send(embed=help_embed)


  async def send_cog_help(self, cog):
    commands_ = [(command.name, command.short_doc) for command in cog.walk_commands() if command.parent is None]
    # サブコマンドがないコマンドの(名前, 説明)のタプルのリスト

    if not commands_:
      message = self.command_not_found(cog.qualified_name)
      await self.get_destination().send(message)
      return
    
    help_embed = discord.Embed(title=f"{cog.qualified_name}カテゴリのコマンド一覧", description=cog.description)
    for name, doc in commands_:
      help_embed.add_field(name=name, value=doc, inline=False)
    await self.get_destination().send(embed=help_embed)
  

  async def send_group_help(self, group):
    help_embed = discord.Embed(title=self.parents_aliases(group), description=group.help)
    for subcommand in group.commands:
      help_embed.add_field(name=subcommand.name, value=subcommand.short_doc, inline=False)
    await self.get_destination().send(embed=help_embed)
  

  async def send_command_help(self, command):
    print(id(self))
    
    help_embed = discord.Embed()
    help_embed.title = self.parents_aliases(command) + " " + command.help.rsplit("\n", 1)[1]
    help_embed.description = command.help.rsplit("\n", 1)[0]
    await self.get_destination().send(embed=help_embed)
