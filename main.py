
TOKEN = "TOKEN HERE"

import discord
import asyncio
from discord.ext import commands
from discord.utils import get

client = commands.Bot(command_prefix = "!", help_command = None)

@client.event
async def on_ready():
  print("CARL by meek#1652\nThe bot has been activated!")

@client.command()
async def help(ctx):
  embedVar = discord.Embed(title="CARL", description="by meek#1652", color=0xFFFFFF)
  embedVar.add_field(name="CARL, or", value = 
    "**C**hannel **A**nd **R**ole **L**inker links a voice channel with a\n" 
    "role. Joining the voice channel will give you the linked role.\n" 
    "Usage: "
    "!link \@role channel_name **or** !link channel_name \@role\n" 
    "*links a role with a channel.*\n"
    "!unlink channel_name\n" 
    "*unlinks all roles with the channel*\n"
    "!show_links\n"
    "*shows all links*", 
    inline=False)
  await ctx.send(embed=embedVar)

def print_embed(title, description, color):
  embed_message = discord.Embed(title=title, description=description, color=color)
  return embed_message

client.links = dict()

@client.command()
@commands.has_permissions(administrator=True)
async def link(ctx, *args):
  full_arg = " ".join(args)
  role_id = full_arg[full_arg.find("<@") : full_arg.find(">") + 1]
  channel_name = full_arg.replace(role_id, "").strip()
  if len(role_id) > 0 and len(channel_name) > 0:
    channel_id = get(ctx.guild.voice_channels, name=channel_name) 
    role_name = ctx.guild.get_role(int(role_id.replace("<@&", "").replace(">", ""))).name
    if role_name is not None:
      if channel_id is not None:
        if channel_name in client.links:
          if role_name in client.links[channel_name]:
            await ctx.send(embed=print_embed(
              "Error!",
             f"The channel \"{channel_name}\" and the role \"{role_name}\" are already linked",
             0xff5733))
            return
          else:
            client.links[channel_name].append(role_name)
        else:
          client.links[channel_name] = [role_name]
        await ctx.send(embed=print_embed(
          "Success!", 
         f"The voice channel \"{channel_name}\" and the role \"{role_name}\" have been **linked**", 
          0x2dc323))
      else:
        await ctx.send(embed=print_embed(
          "Error!", 
         f"\"{channel_name}\" is not a valid voice channel", 
          0xff5733))
    else:
      if channel_id is not None:
        await ctx.send(embed=print_embed( 
          "Error!", 
         f"\"{role_name}\" is not a valid role", 
          0xff5733))
      else:
        await ctx.send(embed=print_embed(
          "Error!", 
         f"\"{channel_name}\" is not a valid voice channel and \"{role_name}\" is not a valid role", 
          0xff5733))
  else:
    await ctx.send(embed=print_embed(
      "Error!",
     f"Misuse of command. Please do !help for assistance",
      0xff5733))

@client.command()
@commands.has_permissions(administrator=True)
async def unlink(ctx, *args):
  channel_name = " ".join(args)
  if channel_name in client.links:
    await ctx.send(embed=print_embed(
      "Success!",
     f"The channel **{channel_name}** and the role(s) **{' & '.join(client.links[channel_name])}** have been **unlinked**.",
      0x2dc323))
    del client.links[channel_name]
  else:
    await ctx.send(embed=print_embed(
      "Error!",
     f"**{channel_name}** is not a valid voice channel",
      0xff5733))

@client.event
async def on_voice_state_update(ctx, before, after):
  previousChannel = before.channel
  newChannel = after.channel
  if previousChannel is not str(newChannel):
    if str(newChannel) in client.links:
      if previousChannel is not None and str(previousChannel) in client.links:
        remove_roles = client.links[str(previousChannel)]
        for role in remove_roles:
          await ctx.remove_roles(get(ctx.guild.roles, name = role))
      add_roles = client.links[str(newChannel)]
      for role in add_roles:
        await ctx.add_roles(get(ctx.guild.roles, name = role))
    else:
      if str(previousChannel) in client.links:
        remove_roles = client.links[str(previousChannel)]
        for role in remove_roles:
          await ctx.remove_roles(get(ctx.guild.roles, name = role))

client.link_pages = list()

@client.command()
async def show_links(ctx):
  display_page = 1
  for link in client.links:
    client.link_pages.append(discord.Embed(title=f"{link} {display_page}/{len(client.links)}", description=" & ".join(client.links[link]), color=0xfffafa))
    display_page += 1
  display = await ctx.send(embed=client.link_pages[0])
  await display.add_reaction("\U00002b05")
  await display.add_reaction("\U000027a1")
  current_page = 0
  reaction = ""
  await asyncio.sleep(1)
  while True:
    try:
      reaction, user = await client.wait_for('reaction_add', timeout=30.0)
      if reaction.emoji == "\U00002b05":
        if current_page > 0:
          current_page -= 1
      elif reaction.emoji == "\U000027a1":
        if current_page < len(client.link_pages) - 1:
          current_page += 1
      await display.edit(embed=client.link_pages[current_page])
    except asyncio.TimeoutError:
      break
  await display.clear_reactions()

client.run(TOKEN)
