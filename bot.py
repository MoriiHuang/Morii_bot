from ast import mod
import asyncio
import os
from loguru import logger
from graia.broadcast import Broadcast
import pkgutil
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, MiraiSession
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler.saya.behaviour import GraiaSchedulerBehaviour
from graia.scheduler import GraiaScheduler
from matplotlib.pyplot import prism
loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:3000",  # 填入 HTTP API 服务运行的地址
        verify_key="hcytsl",  # 填入 verifyKey
        account=3237855048,  # 你的机器人的 qq 号
    )
)
from graia.scheduler import GraiaScheduler
sche = app.create(GraiaScheduler)
from graia.scheduler import timers
@sche.schedule(timers.crontabify('00 23 * * *'))
async def every_minute_speaking(app: Ariadne):
    await app.sendGroupMessage(1072621520, MessageChain.create("熬夜虽好，也不要贪玩哦"))
saya = Saya(bcc)
saya.install_behaviours(
    BroadcastBehaviour(bcc),
    GraiaSchedulerBehaviour(sche)
)
dirs="/Users/lucifer/Desktop/大二下/mirai/modules"
with saya.module_context():
    for module in os.listdir("modules"):
        if os.path.isdir(os.path.join(dirs,module)):
            saya.require(f"modules.{module}")
        else:
            saya.require(f"modules.{module.split('.')[0]}")
    logger.info("saya加载完成")
app.launch_blocking()

