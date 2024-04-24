from classes.data_classes import ReturnData
from utils.log import log

async def ping_def(ctx, bot_class) -> ReturnData:
    """
    Ping command
    :param ctx: Context
    :param bot_class: Bot class
    :return: ReturnData
    """
    log(ctx, 'ping_def', options=locals(), log_type='function', author=ctx.author)

    message = f'**Pong!** Latency: {round(bot_class.latency * 1000)}ms'
    await ctx.reply(message)
    return ReturnData(True, message)
