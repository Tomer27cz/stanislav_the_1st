from classes.data_classes import ReturnData

from utils.source import GetSource
from utils.log import log
from utils.url import get_first_url
from utils.url import get_url_type, extract_yt_id

import commands.voice

import discord
import subprocess
import json

async def get_url_probe_data(url: str) -> (tuple or None, str or None):
    """
    Returns probe data of url
    or None if not found
    :param url: str: url to probe
    :return: tuple(codec, bitrate), url or None, None
    """
    extracted_url = get_first_url(url)
    if extracted_url is None:
        return None, extracted_url

    # noinspection PyBroadException
    try:
        executable = 'ffmpeg'
        exe = executable[:2] + 'probe' if executable in ('ffmpeg', 'avconv') else executable
        args = [exe, '-v', 'quiet', '-print_format', 'json', '-show_streams', '-select_streams', 'a:0', extracted_url]
        output = subprocess.check_output(args, timeout=20)
        codec = bitrate = None

        if output:
            data = json.loads(output)
            streamdata = data['streams'][0]

            codec = streamdata.get('codec_name')
            bitrate = int(streamdata.get('bit_rate', 0))
            bitrate = max(round(bitrate / 1000), 512)
    except Exception:
        codec, bitrate = None, None

    if codec and bitrate:
        return (codec, bitrate), extracted_url

    return None, extracted_url

async def get_url(ctx, url) -> ReturnData:
    """
    :param ctx: Context
    :param url: An input string that is a URL
    :return: ReturnData(bool, str, VideoClass child or None)
    """
    log(ctx, 'get_url', locals(), log_type='function', author=ctx.author)

    if not url:
        message = "`url` is **required**"
        return ReturnData(False, message)

    # Get url type
    url_type, url = get_url_type(url)
    yt_id = extract_yt_id(url)

    if url_type in ['Spotify Playlist', 'Spotify Album', 'Spotify Track', 'Spotify URL']:
        message = 'Spotify URLs are not supported in this bot'
        return ReturnData(False, message)

    # YOUTUBE ----------------------------------------------------------------------------------------------------------

    if url_type == 'YouTube Playlist Video':
        url = url[:url.index('&list=')]
        url_type = 'YouTube Video'

    if url_type == 'YouTube Video' or yt_id is not None:
        url = f"https://www.youtube.com/watch?v={yt_id}"
        return ReturnData(True, 'Video url returned', url)

    if url_type == 'YouTube Playlist':
        message = 'YouTube playlists are not supported in this bot'
        return ReturnData(False, message)

    # URL --------------------------------------------------------------------------------------------------------------

    if url_type == 'String with URL':
        probe, extracted_url = await get_url_probe_data(url)
        if probe:
            return ReturnData(True, 'Probe data returned', extracted_url)

    message = f'`{url}` is not supported!'
    return ReturnData(False, message)

async def play_def(ctx, bot_class, url, mute_response: bool=False) -> ReturnData:
    log(ctx, 'play_def', options=locals(), log_type='function', author=ctx.author)

    response = ReturnData(False, 'Unknown error')

    voice: discord.VoiceClient = ctx.guild.voice_client

    if not voice:
        if ctx.author.voice is None:
            message = "You are **not connected** to a voice channel"
            if not mute_response:
                await ctx.reply(message)
            return ReturnData(False, message)

    if not ctx.interaction.response.is_done():
        await ctx.defer()


    url_response = await get_url(ctx, url)
    if not url_response.response:
        if not mute_response:
            await ctx.reply(url_response.message)
        return url_response

    stream_url = url_response.video

    if not ctx.guild.voice_client:
        join_response = await commands.voice.join_def(ctx, bot_class, None, True)
        voice: discord.VoiceClient = ctx.guild.voice_client
        if not join_response.response:
            if not mute_response:
                await ctx.reply(join_response.message)
            return join_response

    if voice.is_playing():
        voice.stop()

    if voice.is_paused():
        return await commands.voice.resume_def(ctx, bot_class)

    source = await GetSource.create_source(ctx.guild.id, stream_url)
    voice.play(source)

    message = f'Now Playing: `{stream_url}`'
    if not mute_response:
        await ctx.reply(message)
    return ReturnData(True, message)


