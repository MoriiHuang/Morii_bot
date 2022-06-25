from email.headerregistry import Group
import json
import httpx
import random
import asyncio

from pathlib import Path
from loguru import logger
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.scheduler.saya.schema import SchedulerSchema
from graia.scheduler  import timers
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.event.message import Group, GroupMessage
from graia.ariadne.message.parser.twilight import UnionMatch, RegexMatch, RegexResult
from utils.TimeTool import TimeRecorder
from utils.text2image import create_image

from .get_news import Game, Weibo

channel = Channel.current()
weibo = Weibo()
game = Game()

HOME = Path(__file__).parent
print(HOME)
PUSHED_LIST_FILE = HOME.joinpath("pushed_list.json")
print(PUSHED_LIST_FILE)
if PUSHED_LIST_FILE.exists():
    with PUSHED_LIST_FILE.open("r") as f:
        pushed_list = json.load(f)
else:
    with PUSHED_LIST_FILE.open("w") as f:
        pushed_list = {"weibo": None, "game": None}
        json.dump(pushed_list, f, indent=2)


def save_pushed_list():
    with PUSHED_LIST_FILE.open("w") as f:
        json.dump(pushed_list, f, indent=2)
@channel.use(SchedulerSchema(timers.every_custom_hours(6)))
@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))

async def get_weibo_news(app: Ariadne):
    try:
        pushed = pushed_list["weibo"]
        new_id = await weibo.requests_content(0, only_id=True)
        if not pushed:
            pushed_list["weibo"] = [new_id]
            save_pushed_list()
            await asyncio.sleep(1)
            logger.info(f" 原神 微博初始化成功，当前最新微博：{new_id}")
            return
        elif not isinstance(new_id, str) or new_id in pushed:
            return

        pushed_list["weibo"].append(new_id)
        save_pushed_list()
        result, detail_url, pics_list = await weibo.requests_content(0)
        time_rec = TimeRecorder()
        logger.info(f" 原神微博已更新：{new_id}")
        image = await create_image(result, 72)
        msg = [
            Plain("明日方舟更新了新的微博\n"),
            Plain(f"{detail_url}\n"),
            Image(data_bytes=image),
        ] + [Image(url=x) for x in pics_list]
        await app.sendFriendMessage(
            1072621520, MessageChain.create(new_id)
        )
        await app.sendFriendMessage(
            1072621520, MessageChain.create(msg)
        )
        group_list = (
        [await app.getGroup(601981487)]
    )
        for group in group_list:
            await app.sendMessage(group, MessageChain.create(msg))
            await asyncio.sleep(random.uniform(2, 4))

        await app.sendFriendMessage(
            1072621520,
            MessageChain.create([Plain(f"微博推送结束，耗时{time_rec.total()}")]),
        )

    except Exception:
        pass


@channel.use(SchedulerSchema(timers.every_custom_hours(6)))
@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def get_game_news(app: Ariadne):
    pushed = pushed_list["game"] if pushed_list["game"] else []
    try:
        latest_list = await game.get_announce()
    except httpx.HTTPError:
        return
    new_list = list(set(latest_list) - set(pushed))
    print(latest_list)
    if not pushed:
        pushed_list["game"] = latest_list
        save_pushed_list()
        await asyncio.sleep(1)
        logger.info(f"[明日方舟蹲饼] 游戏公告初始化成功，当前共有 {len(latest_list)} 条公告")
        return
    elif not new_list:
        return

    pushed_list["game"] = latest_list
    save_pushed_list()

    group_list = (
        [await app.getGroup(601981487)]
    )

    for announce in new_list:
        time_rec = TimeRecorder()
        logger.info(f"[明日方舟蹲饼] 游戏公告已更新：{announce}")
        image = await game.get_screenshot(announce)
        msg = [Plain("明日方舟更新了新的游戏公告\n"), Image(data_bytes=image)]
        await app.sendFriendMessage(
            1072621520, MessageChain.create(msg)
        )
        for group in group_list:
            await app.sendMessage(group, MessageChain.create(msg))
            await asyncio.sleep(random.uniform(2, 4))

        await app.sendFriendMessage(
            1072621520,
            MessageChain.create([Plain(f"游戏公告推送结束，耗时{time_rec.total()}")]),
        )

        await asyncio.sleep(3)