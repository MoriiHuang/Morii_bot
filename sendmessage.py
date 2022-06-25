import asyncio
from typing import Optional, Union, Iterable
from graia.ariadne.context import ariadne_ctx
from graia.ariadne.model import BotMessage, Group, Member, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Source, Element
from graia.ariadne.exception import UnknownTarget, UnknownError


async def safeSendGroupMessage(
    target: Union[Group, int],
    message: Union[MessageChain, Iterable[Element], Element, str],
    quote: Optional[Union[Source, int]] = None,
) -> BotMessage:
    app = ariadne_ctx.get()
    if not isinstance(message, MessageChain):
        message = MessageChain.create(message)
    try:
        return await app.sendGroupMessage(target, message, quote=quote)
    except UnknownTarget:
        msg = []
        for element in message.__root__:
            if isinstance(element, At):
                member = await app.getMember(target, element.target)
                if member:
                    name = member.name
                else:
                    name = str(element.target)
                msg.append(Plain(name))
                continue
            msg.append(element)
        try:
            return await app.sendGroupMessage(
                target, MessageChain.create(msg), quote=quote
            )
        except UnknownTarget:
            try:
                return await app.sendGroupMessage(target, MessageChain.create(msg))
            except UnknownError:
                await asyncio.sleep(15)
                try:
                    return await app.sendGroupMessage(target, MessageChain.create(msg))
                except UnknownError:
                    await app.quitGroup(target)
                    
                    
async def autoSendMessage(
    target: Union[Member, Friend, str],
    message: Union[MessageChain, Iterable[Element], Element, str],
    quote: Optional[Union[Source, int]] = None,
) -> BotMessage:
    """根据输入的目标类型自动选取发送好友信息或是群组信息"""
    app = ariadne_ctx.get()
    if isinstance(target, str):
        target = int(target)
    if not isinstance(message, MessageChain):
        message = MessageChain.create(message)
    if isinstance(target, Member):
        return await app.sendGroupMessage(target, message, quote=quote)
    elif isinstance(target, (Friend, int)):
        return await app.sendFriendMessage(target, message, quote=quote)