import os

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

channels = []
notification_channel = None
num_of_vc_members = {}


def is_text_channel(channel):
    return isinstance(channel, discord.TextChannel)


def is_voice_channel(channel):
    return isinstance(channel, discord.VoiceChannel)


def set_channels():
    global channels
    channels = bot.get_all_channels()


def set_notification_channel():
    global notification_channel
    DEFAULT_NOTIFICATION_CHANNEL_NAME = '一般'
    notification_channel_name = os.environ.get(
        'NOTIFICATION_CHANNEL_NAME',
        DEFAULT_NOTIFICATION_CHANNEL_NAME)
    for channel in channels:
        if channel.name == notification_channel_name and is_text_channel(channel):
            notification_channel = bot.get_channel(channel.id)
            break


def set_num_of_vc_members():
    global num_of_vc_members
    vcs = []
    for channel in channels:
        if is_voice_channel(channel):
            vcs.append(channel)
    for vc in vcs:
        num_of_vc_members[vc.id] = len(vc.members)


def init():
    set_channels()
    set_notification_channel()
    set_num_of_vc_members()


@bot.event
async def on_ready():
    init()
    print(f'{bot.user.display_name} bot is ready!')


@bot.event
async def on_voice_state_update(member, before, after):
    global num_of_vc_members

    # Ignore events other than joining and exiting from voice channels
    if before.channel == after.channel:
        return

    # Someone has joined a voice channel
    if after.channel is not None and is_voice_channel(after.channel):
        target_vc = after.channel
        num_of_vc_members[target_vc.id] = len(target_vc.members)
        if num_of_vc_members[target_vc.id] == 1:
            await notification_channel.send(
                '@everyone '
                f'{member.display_name}が{target_vc.name}チャンネルで通話を開始しました！')
        return

    # Someone has exited from a voice channel
    if before.channel is not None and is_voice_channel(before.channel):
        target_vc = before.channel
        num_of_vc_members[target_vc.id] = len(target_vc.members)
        if num_of_vc_members[target_vc.id] == 0:
            await notification_channel.send(
                f'@everyone {target_vc.name}チャンネルでの通話が終了しました')


@bot.command()
async def echo(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def sync(ctx):
    init()
    await ctx.send(
        f'{bot.user.display_name} botの状態を最新に更新しました！')

bot.run(os.environ['DISCORD_BOT_TOKEN'])
