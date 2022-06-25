from importlib.resources import path
from datetime import date, datetime
from io import BytesIO
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from urllib.parse import quote
from graia.ariadne.message.element import *
import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain,Quote,Source
from graia.ariadne.message.parser.base import Mention,DetectPrefix,DetectSuffix
from graia.ariadne.message.parser.twilight import(FullMatch, MatchResult,SpacePolicy,
                                                   Twilight, WildcardMatch,RegexMatch)
from graia.ariadne.model import Friend,Group, MiraiSession,Member
from typing import Union, final
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.message.element import At,Plain,Voice,Image
from numpy import random
app = Ariadne(
    connect_info=MiraiSession(
        host="http://localhost:3000",  # 填入 HTTP API 服务运行的地址
        verify_key="hcytsl",  # 填入 verifyKey
        account=3237855048,  # 你的机器人的 qq 号
    )
)
bcc = app.broadcast
@bcc.receiver(GroupMessage)
async def setu(app: Ariadne, group: Group, message: MessageChain):
   if str(message) == "你好":
      await app.sendMessage(
         group,
         MessageChain.create(f"不要说{message.asDisplay()}，来点涩图"),
      )
@bcc.receiver(GroupMessage)
async def lmy(app: Ariadne, group: Group, message: MessageChain):
   if str(message) == "lmy":
      await app.sendMessage(
         group,
         MessageChain.create(f"hcy是lmy爸爸"),
      )
@bcc.receiver(GroupMessage, decorators=[Mention(target=1072621520)])  # target: int | str
async def on_mention(app: Ariadne, group: Group):
    await app.sendMessage(group, MessageChain.create("你找我主人有什么事吗"))
@bcc.receiver(GroupMessage, decorators=[Mention(target="Morii")])  # target: int | str
async def on_mention(app: Ariadne, group: Group):
    await app.sendMessage(group, MessageChain.create("你找我主人有什么事吗"))
@bcc.receiver(GroupMessage, decorators=[Mention(target="moriiのbot")])  # 注意要实例化
async def on_mention_me(app: Ariadne, group: Group, member: Member):
    await app.sendMessage(group, MessageChain.create(At(member.id), "你jb谁啊？"))
@bcc.receiver(GroupMessage, decorators=[Mention(target=app.account)])  # 注意要实例化
async def on_mention_me(app: Ariadne, group: Group, member: Member):
    await app.sendMessage(group, MessageChain.create(At(member.id), "叫我？"))
@bcc.receiver(GroupMessage, decorators=[DetectSuffix('涩')])
async def on_message1(group:Group,chain: MessageChain): # chain 必定以 "启动" 结尾
    await app.sendMessage(group, MessageChain.create("好的，主人"))
@bcc.receiver(
    GroupMessage,
    dispatchers=[Twilight.from_command("涩图来")],
)
async def test(app: Ariadne, group: Group):
    num=random.randint(0,26)
    path1="/Users/lucifer/PycharmProjects/Crawler/xpath/原神/{}.jpeg".format(num)
    await app.sendGroupMessage(
        group,
        MessageChain.create(
            Image(path=path1)
        ),
    )
@bcc.receiver(
    GroupMessage,
    dispatchers=[Twilight(
        [FullMatch("anime"),
         WildcardMatch(optional=True) @ "para"]
    )],
)
async def anime(app: Ariadne, group: Group, para: MatchResult):
    today = int(datetime.fromisoformat(date.today().isoformat()).timestamp())
    date2ts = {'yesterday': today-86400, '':today, 'tomorrow': today+86400}
    d = para.result.asDisplay().strip() if para.matched else ''

    if d in date2ts:
        date_ts = date2ts[d]
    else:
        await app.sendGroupMessage(group, MessageChain.create('未知时间'))
        return

    async with aiohttp.ClientSession() as session:
        async with session.get('https://bangumi.bilibili.com/web_api/timeline_global') as r:
            result = (await r.json())['result']
            data = next(anime_ts['seasons'] for anime_ts in result if anime_ts['date_ts'] == date_ts)
        final_back = IMG.new("RGB",(1200,300 * len(data)),(40,41,35))
        final_draw = ImageDraw.Draw(final_back)
        for n, single in enumerate(data):
            async with session.get(single['square_cover']) as f:
                pic = IMG.open(BytesIO(await f.read()))
            if pic.size != (240, 240):
                pic = pic.resize((240, 240), IMG.ANTIALIAS)
            mask = IMG.new("L", (480,480), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0,0,480,480), 50, 255)
            final_back.paste(pic, (30,30+300*n,270,270+300*n), mask=mask.resize((240, 240), IMG.ANTIALIAS))
            ttf = ImageFont.truetype('src/font/SourceHanSans-Medium.otf', 60)
            ellipsis_size = ttf.getsize('...')[0]
            if ttf.getsize(single['title'])[0] >= 900:
                while ttf.getsize(single['title'])[0] > 900 - ellipsis_size:
                    single['title'] = single['title'][:-1]
                single['title'] = single['title'] + '...'
            final_draw.text((300, 50+300*n), single['title'], font=ttf, fill=(255,255,255))
            final_draw.text((300, 150+300*n), single['pub_time'], font=ttf, fill=(255,255,255))
            final_draw.text((300+ttf.getsize(single['pub_time'])[0]+30, 150+300*n),
                single['pub_index'] if 'pub_index' in single else single['delay_index']+single['delay_reason'], 
                font=ttf, fill=(0,160,216))
            
        final_back.save(out := BytesIO(), format='JPEG')
    await app.sendGroupMessage(group, MessageChain.create([
        Image(data_bytes=out.getvalue())]))
@bcc.receiver(
    GroupMessage,
    dispatchers=[Twilight(
        [FullMatch("bangumi").space(SpacePolicy.FORCE),
         WildcardMatch() @ "para"]
    )],
)
async def anime(app: Ariadne, group: Group, para: MatchResult):
    bangumi_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "\
                  "AppleWebKit/537.36 (KHTML, like Gecko) "\
                  "Chrome/84.0.4147.135 Safari/537.36"}
    url = 'https://api.bgm.tv/search/subject/{}?type=2&responseGroup=Large&max_results=1'.format(
        quote(para.result.asDisplay().strip()))
    async with aiohttp.request("GET", url, headers = bangumi_headers) as r:
        data = await r.json()

    if "code" in data.keys() and data["code"] == 404:
        await app.sendGroupMessage(group, MessageChain.create('sorry,搜索不到相关信息'))
        return

    detail_url = f'https://api.bgm.tv/subject/{data["list"][0]["id"]}?responseGroup=medium'
    async with aiohttp.request("GET", detail_url) as r:
        data = await r.json()
    async with aiohttp.request("GET", data["images"]["large"]) as r:
        img = await r.read()
    await app.sendGroupMessage(group, MessageChain.create([
        Image(data_bytes=img),
        Plain(text=f"名字:{data['name_cn']}({data['name']})\n"),
        Plain(text=f"简介:{data['summary']}\n"),
        Plain(text=f"bangumi评分:{data['rating']['score']}(参与评分{data['rating']['total']}人)\n"),
        Plain(text=f"bangumi排名:{data['rank']}" if 'rank' in data else '')
        ]))
@bcc.receiver(
    GroupMessage,
    dispatchers=[
    Twilight([RegexMatch(r"(来个老婆|随机老婆)$")])]
)
async def random_wife(app: Ariadne, message: MessageChain, group: Group):
    await app.sendGroupMessage(
        group,
        MessageChain([Image(url=f"https://www.thiswaifudoesnotexist.net/example-{random.randint(1, 100000)}.jpg")]),
        quote=message.getFirst(Source)
    )
app.launch_blocking()