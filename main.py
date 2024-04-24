from utils.log import send_to_admin

from commands.general import *
from commands.player import *
from commands.voice import *

from discord.ext import commands as dc_commands
from discord import app_commands

import discord.ext.commands
import asyncio

import config

my_id = config.OWNER_ID
bot_id = config.CLIENT_ID
prefix = config.PREFIX
d_id = 349164237605568513

# ---------------- Bot class ------------

class Bot(dc_commands.Bot):
    """
    Bot class

    This class is used to create the bot instance.
    """

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=prefix, intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            log(None, "Trying to sync commands")
            await self.tree.sync()
            log(None, f"Synced slash commands for {self.user}")
        await bot.change_presence(activity=discord.Game(name=f"/help"))
        log(None, f'Logged in as:\n{bot.user.name}\n{bot.user.id}')

    async def on_guild_join(self, guild_object):
        # log
        log_msg = f"Joined guild ({guild_object.name})({guild_object.id}) with {guild_object.member_count} members and {len(guild_object.voice_channels)} voice channels"
        log(None, log_msg)

        # send log to admin
        await send_to_admin(self, log_msg)

        # get text channels
        text_channels = guild_object.text_channels
        sys_channel = guild_object.system_channel

        # send welcome message in system channel or first text channel
        message = f"Hello **`{guild_object.name}`**! I am `{self.user.display_name}`. Thank you for inviting me.\n\nTo see what commands I have available type `/help`\n\nIf you have any questions, you can DM my developer <@!{config.DEVELOPER_ID}>#4272"
        if sys_channel is not None:
            if sys_channel.permissions_for(guild_object.me).send_messages:
                await sys_channel.send(message)
        else:
            await text_channels[0].send(message)

    async def on_guild_remove(self, guild_object):
        # log
        log_msg = f"Left guild ({guild_object.name})({guild_object.id}) with {guild_object.member_count} members and {len(guild_object.voice_channels)} voice channels"
        log(None, log_msg)

        # send log to admin
        await send_to_admin(self, log_msg)

    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
        guild_id = member.guild.id

        if voice_state is not None and len(voice_state.channel.members) == 1:
            voice_state.stop()
            await voice_state.disconnect()
            log(guild_id, "-->> Disconnecting when last person left <<--")

        if not member.id == self.user.id:
            return

        elif before.channel is None:
            # get voice client
            voice = after.channel.guild.voice_client

            # initialize loop
            time_var = 0
            while True:
                # check every second
                await asyncio.sleep(5)

                # increase time_var
                time_var += 5

                # check if bot is playing and not paused
                if voice.is_playing() and not voice.is_paused():
                    time_var = 0  # reset time_var

                # check if time_var is greater than buffer
                if time_var >= 30:
                    # stop playing and disconnect
                    voice.stop()
                    await voice.disconnect()

                    log(guild_id, "-->> Disconnecting after 30 seconds of inactivity <<--")

                # check if bot is disconnected
                if not voice.is_connected():
                    break  # break loop

    async def on_command_error(self, ctx, error):
        # get error traceback
        error_traceback = traceback.format_exception(type(error), error, error.__traceback__)
        error_traceback = ''.join(error_traceback)

        err_msg = f"Error: ({error})\nType: ({type(error)})\nAuthor: ({ctx.author})\nCommand: ({ctx.command})\nKwargs: ({ctx.kwargs})"

        if isinstance(error, discord.errors.Forbidden):
            log(ctx, 'error.Forbidden', {'error': error}, log_type='error', author=ctx.author)
            await send_to_admin(self, err_msg, file=True)
            await ctx.send("The command failed because I don't have the required permissions.\n Please give me the required permissions and try again.")
            return

        if isinstance(error, dc_commands.CheckFailure):
            log(ctx, err_msg, log_type='error', author=ctx.author)
            await send_to_admin(self, err_msg, file=True)
            await ctx.reply(f"（ ͡° ͜ʖ ͡°)つ━☆・。\n"
                            f"⊂　　 ノ 　　　・゜+.\n"
                            f"　しーＪ　　　°。+ ´¨)\n"
                            f"　　　　　　　　　.· ´¸.·´¨) ¸.·*¨)\n"
                            f"　　　　　　　　　　(¸.·´ (¸.·' ☆ **Fuck off**\n"
                            f"*You dont have permission to use this command*")
            return

        if isinstance(error, dc_commands.MissingPermissions):
            log(ctx, err_msg, log_type='error', author=ctx.author)
            await send_to_admin(self, err_msg, file=True)
            await ctx.reply(f'Bot does not have permissions to execute this command correctly - {error}')
            return

        if 'Video unavailable.' in str(error):
            # log(ctx, err_msg, log_type='error', author=ctx.author)
            try:
                error = error.original.original
            except AttributeError:
                pass

            await ctx.reply(f'{error} -> It *may be* ***GeoBlocked*** in `Google Cloud - USA` (bot server)')
            return

        err_msg += f"\nTraceback: \n{error_traceback}"
        log(ctx, err_msg, log_type='error', author=ctx.author)

        await send_to_admin(self, err_msg, file=True)
        await ctx.reply(f"{error}   {bot.get_user(config.DEVELOPER_ID).mention}", ephemeral=True)

    async def on_message(self, message):
        # on every message
        if message.author == bot.user:
            return

        # check if message is a DM
        if not message.guild:
            # send DM to ADMIN
            await send_to_admin(self, f"<@!{message.author.id}> tied to DM me with this message `{message.content}`")
            try:
                # respond to DM
                await message.channel.send(
                    f"I'm sorry, but I only work in servers.\n\n"
                    f""
                    f"If you want me to join your server, you can invite me with this link: {config.INVITE_URL}\n\n"
                    f""
                    f"If you have any questions, you can DM my developer <@!{config.DEVELOPER_ID}>#4272")
                return

            except discord.errors.Forbidden:
                return

        await bot.process_commands(message)

# ---------------------------------------------- LOAD ------------------------------------------------------------------

log(None, "--------------------------------------- NEW / REBOOTED ----------------------------------------")

# ---------------------------------------------- BOT -------------------------------------------------------------------

bot = Bot()

log(None, 'Discord API initialized')

# --------------------------------------- COMMANDS --------------------------------------------------

@bot.hybrid_command(name='play', with_app_command=True, description="Play a YouTube Song", help="Play a YouTube Song", extras={'category': 'player'})
@app_commands.describe(url="URL of the video to play (YouTube)")
async def play(ctx: dc_commands.Context, url: str):
    log(ctx, 'play', options=locals(), log_type='command', author=ctx.author)
    await play_def(ctx, bot, url)

@bot.hybrid_command(name='stop', with_app_command=True, description="Stop the current song", help="Stop the current song", extras={'category': 'voice'})
async def stop(ctx: dc_commands.Context):
    log(ctx, 'stop', options=locals(), log_type='command', author=ctx.author)
    await stop_def(ctx, bot)
#
# @bot.hybrid_command(name='pause', with_app_command=True, description="Pause the current song", help="Pause the current song", extras={'category': 'voice'})
# async def pause(ctx: dc_commands.Context):
#     log(ctx, 'pause', options=locals(), log_type='command', author=ctx.author)
#     await pause_def(ctx, bot)

# @bot.hybrid_command(name='resume', with_app_command=True, description="Resume the current song", help="Resume the current song", extras={'category': 'voice'})
# async def resume(ctx: dc_commands.Context):
#     log(ctx, 'resume', options=locals(), log_type='command', author=ctx.author)
#     await resume_def(ctx, bot)

@bot.hybrid_command(name='join', with_app_command=True, description="Join a voice channel", help="Join a voice channel", extras={'category': 'voice'})
@app_commands.describe(channel="Channel to join")
async def join(ctx: dc_commands.Context, channel: discord.VoiceChannel = None):
    log(ctx, 'join', options=locals(), log_type='command', author=ctx.author)
    await join_def(ctx, bot, channel_id=channel.id if channel else None)

@bot.hybrid_command(name='disconnect', with_app_command=True, description="Disconnect from voice channel", help="Disconnect from voice channel", extras={'category': 'voice'})
async def disconnect(ctx: dc_commands.Context):
    log(ctx, 'disconnect', options=locals(), log_type='command', author=ctx.author)
    await disconnect_def(ctx, bot)

@bot.hybrid_command(name='ping', with_app_command=True, description="Ping the bot", help="Ping the bot", extras={'category': 'general'})
async def ping_command(ctx: dc_commands.Context):
    log(ctx, 'ping', options=locals(), log_type='command', author=ctx.author)
    await ping_def(ctx, bot)


# --------------------------------------------- HELP COMMAND -----------------------------------------------------------

bot.remove_command('help')

@bot.hybrid_command(name='help', with_app_command=True, description="Get help on a command", help="Get help on a command", extras={'category': 'general'})
async def help_command(ctx: dc_commands.Context, command_name: str = None):
    log(ctx, 'help', options=locals(), log_type='command', author=ctx.author)
    gi = ctx.guild.id

    embed = discord.Embed(title="Commands", description=f"Use `/help <command>` to get help on a command | Prefix: `{prefix}`")

    command_dict = {}
    command_name_dict = {}
    for command in bot.commands:
        if command.hidden:
            continue

        command_name_dict[command.name] = command

        category = command.extras.get('category', 'No category')
        if category not in command_dict:
            command_dict[category] = []

        command_dict[category].append(command)

    if not command_name:
        for category in command_dict.keys():
            message = ''

            for command in command_dict[category]:
                add = f'`{command.name}` - {command.description} \n'

                if len(message + add) > 1024:
                    embed.add_field(name=f"**{category.capitalize()}**", value=message, inline=False)
                    message = ''
                    continue

                message = message + add

            embed.add_field(name=f"**{category.capitalize()}**", value=message, inline=False)

        await ctx.send(embed=embed)
        return

    if command_name not in command_name_dict:
        await ctx.send('Command not found')
        return

    command = command_name_dict[command_name]

    embed = discord.Embed(title=command.name, description=command.description)
    # noinspection PyProtectedMember
    for key, value in command.app_command._params.items():
        embed.add_field(name=f"`{key}` - {value.description}", value=f'Required": `{value.required}` | Default: `{value.default}` | Type: `{value.type}`', inline=False)

    await ctx.send(embed=embed)

# --------------------------------------------------- APP --------------------------------------------------------------

if __name__ == '__main__':
    bot.run(config.BOT_TOKEN)
