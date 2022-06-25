
from numpy import random
from graia.ariadne import get_running
import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend,Group, MiraiSession
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.adapter import Adapter
from graia.ariadne.message.element import *
from arclet.alconna import AlconnaString
from arclet.alconna import Arpamar
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch, MatchResult,RegexMatch
from graia.ariadne.model import Group, Member,Friend
from PIL import Image as IMG
import aiohttp
from pathlib import Path
from io import BytesIO
from graia.saya import Saya
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from graiax import silkcoder
channel=Channel.current()
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch(r"hentai"),
                ]
            )
        ],
    )
)
async def hentai(app:Ariadne,group: Group, message: MessageChain):
    audio_bytes = await silkcoder.encode("/Users/lucifer/Desktop/大二下/mirai/statics/voice/kugimiya/37_hentai.mp3")
    await app.sendMessage(
            group,
            MessageChain.create(Voice(data_bytes=audio_bytes))
            )