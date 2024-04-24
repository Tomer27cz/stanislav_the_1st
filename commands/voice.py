from classes.data_classes import ReturnData

from utils.log import log
from utils.discord import get_voice_client

from discord.ext import commands as dc_commands
import discord
import traceback


async def stop_def(ctx, bot_class, mute_response: bool = False) -> ReturnData:
    """
    Stops player
    :param ctx: Context
    :param bot_class: Bot class
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'stop_def', options=locals(), log_type='function', author=ctx.author)

    voice: discord.voice_client.VoiceClient = get_voice_client(bot_class.voice_clients, guild=ctx.guild)

    if not voice:
        message = "Bot is not connected to a voice channel"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

    voice.stop()

    message = "Player **stopped!**"
    if not mute_response:
        await ctx.reply(message, ephemeral=True)
    return ReturnData(True, message)

async def pause_def(ctx, bot_class, mute_response: bool = False) -> ReturnData:
    """
    Pause player
    :param ctx: Context
    :param bot_class: Bot class
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'pause_def', options=locals(), log_type='function', author=ctx.author)

    voice: discord.voice_client.VoiceClient = get_voice_client(bot_class.voice_clients, guild=ctx.guild)

    if not voice:
        message = "Bot is not connected to a voice channel"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

    if voice.is_playing():
        voice.pause()
        message = "Player **paused!**"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(True, message)

    if voice.is_paused():
        message = "Player **already paused!**"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

    message = 'No audio playing'
    if not mute_response:
        await ctx.reply(message, ephemeral=True)
    return ReturnData(False, message)

async def resume_def(ctx, bot_class, mute_response: bool = False) -> ReturnData:
    """
    Resume player
    :param ctx: Context
    :param bot_class: Bot class
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'resume_def', options=locals(), log_type='function', author=ctx.author)

    voice: discord.voice_client.VoiceClient = get_voice_client(bot_class.voice_clients, guild=ctx.guild)

    if not voice:
        message = "Bot is not connected to a voice channel"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

    if voice.is_paused():
        voice.resume()
        message = "Player **resumed!**"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(True, message)

    if voice.is_playing():
        message = "Player **already resumed!**"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

    message = 'No audio playing'
    if not mute_response:
        await ctx.reply(message, ephemeral=True)
    return ReturnData(False, message)

async def join_def(ctx, bot_class, channel_id=None, mute_response: bool = False) -> ReturnData:
    """
    Join voice channel
    :param ctx: Context
    :param bot_class: Bot class
    :param channel_id: id of channel to join
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'join_def', options=locals(), log_type='function', author=ctx.author)

    # define author channel (for ide)
    author_channel = None

    if not channel_id:
        if ctx.author.voice:
            # get author voice channel
            author_channel = ctx.author.voice.channel

            if ctx.voice_client:
                # if bot is already connected to author channel return True
                if ctx.voice_client.channel == author_channel:
                    message = "I'm already in this channel"
                    if not mute_response:
                        await ctx.reply(message, ephemeral=True)
                    return ReturnData(True, message)
        else:
            # if author is not connected to a voice channel return False
            message = "You are **not connected** to a voice channel"
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

    try:
        # get voice channel
        if author_channel:
            voice_channel = author_channel
        else:
            voice_channel = bot_class.get_channel(int(channel_id))

        # check if bot has permission to join channel
        if not voice_channel.permissions_for(ctx.guild.me).connect:
            message = "I don't have permission to join this channel"
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

        # check if bot has permission to speak in channel
        if not voice_channel.permissions_for(ctx.guild.me).speak:
            message = "I don't have permission to speak in this channel"
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

        # check if the channel is empty
        if not len(voice_channel.members) > 0:
            message = "The channel is empty"
            await ctx.reply(message, ephemeral=True)
            return ReturnData(False, message)

        # disconnect from voice channel if connected
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect(force=True)
        # connect to voice channel
        await voice_channel.connect()
        # deafen bot
        await ctx.guild.change_voice_state(channel=voice_channel, self_deaf=True)

        message = f"Joined voice channel: `{voice_channel.name}`"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(True, message)

    except (discord.ext.commands.errors.CommandInvokeError, discord.errors.ClientException, AttributeError, ValueError,
            TypeError):
        log(ctx, "------------------------------- join -------------------------")
        tb = traceback.format_exc()
        log(ctx, tb)
        log(ctx, "--------------------------------------------------------------")

        message = "Channel **doesn't exist** or bot doesn't have **sufficient permission** to join"
        await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)

async def disconnect_def(ctx, bot_class, mute_response: bool = False) -> ReturnData:
    """
    Disconnect bot from voice channel
    :param ctx: Context
    :param bot_class: Bot class
    :param mute_response: Should bot response be muted
    :return: ReturnData
    """
    log(ctx, 'disconnect_def', options=locals(), log_type='function', author=ctx.author)

    if ctx.guild.voice_client:
        await stop_def(ctx, bot_class, mute_response=True)

        channel = ctx.guild.voice_client.channel
        await ctx.guild.voice_client.disconnect(force=True)

        message = f"Left voice channel: `{channel}`"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(True, message)
    else:
        message = "Bot is **not** in a voice channel"
        if not mute_response:
            await ctx.reply(message, ephemeral=True)
        return ReturnData(False, message)
