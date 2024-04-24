import discord

def get_voice_client(iterable, **attrs) -> discord.VoiceClient:
    """
    Gets voice_client from voice_clients list
    :param iterable: list
    :return: discord.VoiceClient
    """
    from operator import attrgetter

    # noinspection PyShadowingNames
    def _get(iterable, /, **attrs):
        # global -> local
        _all = all
        attrget = attrgetter

        # Special case the single element call
        if len(attrs) == 1:
            k, v = attrs.popitem()
            pred = attrget(k.replace('__', '.'))
            return next((elem for elem in iterable if pred(elem) == v), None)

        converted = [(attrget(attr.replace('__', '.')), value) for attr, value in attrs.items()]
        for elem in iterable:
            if _all(pred(elem) == value for pred, value in converted):
                return elem
        return None

    # noinspection PyShadowingNames
    async def _aget(iterable, /, **attrs):
        # global -> local
        _all = all
        attrget = attrgetter

        # Special case the single element call
        if len(attrs) == 1:
            k, v = attrs.popitem()
            pred = attrget(k.replace('__', '.'))
            async for elem in iterable:
                if pred(elem) == v:
                    return elem
            return None

        converted = [(attrget(attr.replace('__', '.')), value) for attr, value in attrs.items()]

        async for elem in iterable:
            if _all(pred(elem) == value for pred, value in converted):
                return elem
        return None


    return (
        _aget(iterable, **attrs)  # type: ignore
        if hasattr(iterable, '__aiter__')  # isinstance(iterable, collections.abc.AsyncIterable) is too slow
        else _get(iterable, **attrs)  # type: ignore
    )
