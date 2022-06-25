import asyncio
from graia.ariadne.app import Ariadne
from saucenao_api import AIOSauceNao
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt.waiter import Waiter
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.interrupt import InterruptControl
from saucenao_api.errors import SauceNaoApiError
from graia.ariadne.message.element import At, Plain, Image, Source
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, ElementMatch,MatchResult
from graia.ariadne.model import Friend,Group, MiraiSession,Member
from sendmessage import safeSendGroupMessage
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Saya
saya=Saya.current()
channel=  Channel.current()
bcc=saya.broadcast
I_RUNING = False
WAITING = []
saucenao_usage = None
async def member1():
    return True
inc=InterruptControl(bcc)
@channel.use(
    ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [   "head"@FullMatch("以图搜图"),
            "enter"@FullMatch("\n", optional=True),
            "img"@ElementMatch(Image, optional=True),]
    )],
))
async def saucenao(group: Group, member: Member, img: ElementMatch, source: Source):
    @Waiter.create_using_function(
        listening_events=[GroupMessage]
    )
    async def waiter1(
        waiter1_group: Group, waiter1_member: Member, waiter1_message: MessageChain
    ):  
        print("hao")
        if all([waiter1_group.id == group.id, waiter1_member.id == member.id]):
            waiter1_saying = waiter1_message.asDisplay()
            if waiter1_saying == "取消":
                return False
            elif waiter1_message.has(Image):
                return waiter1_message.getFirst(Image).url
            else:
                await safeSendGroupMessage(group, MessageChain.create([Plain("请发送图片")]))

    global I_RUNING
    if I_RUNING:
        await safeSendGroupMessage(
            group, MessageChain.create([Plain("以图搜图正在运行，请稍后再试")])
        )
    else:
        if I_RUNING:
            image_url = img.result.url
        else:
            WAITING.append(member.id)
            waite = await safeSendGroupMessage(
                group, MessageChain.create([Plain("请发送图片以继续，发送取消可终止搜图")])
            )
            try:
                image_url = await asyncio.wait_for(inc.wait(waiter1), timeout=20)
                print(image_url)
                if not image_url:
                    WAITING.remove(member.id)
                    return await safeSendGroupMessage(
                        group, MessageChain.create([Plain("已取消")])
                    )
            except asyncio.TimeoutError:
                WAITING.remove(member.id)
                return await safeSendGroupMessage(
                    group, MessageChain.create([Plain("等待超时")]), quote=waite.messageId
                )
        if await member1():
                I_RUNING = True
                await safeSendGroupMessage(
                    group, MessageChain.create([Plain("正在搜索，请稍后")]), quote=source.id
                )
                async with AIOSauceNao(
                    "0167e9bd7b16777a6c2818dc9250b9f5ad9c2dc5"
                ) as snao:
                    try:
                        results = await snao.from_url(image_url)
                    except SauceNaoApiError as e:
                        I_RUNING = False
                        return await safeSendGroupMessage(
                            group,
                            MessageChain.create([Plain(f"搜索失败 {type(e)} {str(e)}")]),
                        )
                global saucenao_usage
                saucenao_usage = {
                    "short": results.short_remaining,
                    "long": results.long_remaining,
                }

                results_list = []
                for results in results.results:
                    url_list = []
                    for url in results.urls:
                        url_list.append(url)
                    if len(url_list) == 0:
                        continue
                    urls = "\n".join(url_list)
                    results_list.append(
                        f"相似度：{results.similarity}%\n标题：{results.title}\n节点名：{results.index_name}\n链接：{urls}"
                    )

                if len(results_list) == 0:
                    await safeSendGroupMessage(
                        group, MessageChain.create([Plain("未找到有价值的数据")]), quote=source.id
                    )
                    I_RUNING = False
                else:
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create(
                            [Plain("\n==================\n".join(results_list))]
                        ),
                        quote=source.id,
                    )
                    I_RUNING = False
