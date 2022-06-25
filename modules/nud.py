import imp
from numpy import random
from graia.ariadne import get_running
import requests
import pymysql
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
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch, MatchResult
from graia.ariadne.model import Group, Member,Friend
from PIL import Image as IMG
import aiohttp
from pathlib import Path
from io import BytesIO
from graia.saya import Saya
from graia.saya.channel import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
frame_spec = [
    [27, 31, 86, 90],
    [22, 36, 91, 90],
    [18, 41, 95, 90],
    [22, 41, 91, 91],
    [27, 28, 86, 91]
]
NoneType = type(None)
try:
    conn = pymysql.connect(host="101.132.109.217",
                            port=3306,
                            user="ieei",
                            passwd="Diangongdao_B",
                            charset="utf8",
                            db="Final_Homework")
    cursor = conn.cursor()
except:
    print('Fail to connect to the database.')
    exit()

# 挤压偏移量

# 最大挤压时头像实际位置与上述描述相差的良
squish_factor = [
    (0, 0, 0, 0),
    (-7, 22, 8, 0),
    (-8, 30, 9, 6),
    (-3, 21, 5, 9),
    (0, 0, 0, 0)
]
# 最大挤压时每一帧模板向下偏移的量
squish_translation_factor = [0, 20, 34, 21, 0]
def make_petpet(file, squish=0):
    profile_pic = IMG.open(file)
    hands = IMG.open(Path(__file__).parent/'sprite.png')
    gifs = []
    for i,spec in enumerate(frame_spec):
        # 将位置添加偏移量
        for j, s in enumerate(spec):
            spec[j] = int(s + squish_factor[i][j] * squish)
        hand = hands.crop((112*i,0,112*(i+1),112))
        reprofile = profile_pic.resize(
            (int((spec[2] - spec[0]) * 1.2), int((spec[3] - spec[1]) * 1.2)),
            IMG.ANTIALIAS)
        gif_frame = IMG.new('RGB', (112, 112), (255, 255, 255))
        gif_frame.paste(reprofile, (spec[0], spec[1]))
        gif_frame.paste(hand, (0, int(squish * squish_translation_factor[i])), hand)
        gifs.append(gif_frame)
    gifs[0].save(
        ret := BytesIO(),
        format='gif',
        save_all=True, append_images=gifs,
        duration=0.05, transparency=0)
    return ret.getvalue()
channel=Channel.current()
@channel.use(ListenerSchema(listening_events= [NudgeEvent]))
async def getup(app: Ariadne,event: NudgeEvent):
        if(event.context_type=="group"):
            await app.sendGroupMessage(
                event.group_id,
                MessageChain.create(f'戳什么戳，要我cao你吗')
            )
        if(event.context_type=="friend"):
            await app.sendFriendMessage(
                event.friend_id,
                MessageChain.create(Image(url="https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpic4.zhimg.com%2Fv2-223a07339e845c3073aac5852cee50de_1200x500.jpg&refer=http%3A%2F%2Fpic4.zhimg.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1650273419&t=9a052f02b54e52426574aa133c458d2e"))
            )
@channel.use(ListenerSchema(listening_events= [GroupMessage]))
async def setu(app: Ariadne, group: Group, message: MessageChain):
    if str(message) == "来点色图":
        print(group)
        await app.sendMessage(
            group,
            MessageChain.create(Image(url="https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpic4.zhimg.com%2Fv2-223a07339e845c3073aac5852cee50de_1200x500.jpg&refer=http%3A%2F%2Fpic4.zhimg.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1650273419&t=9a052f02b54e52426574aa133c458d2e"))
        )
# SetuFind = AlconnaString(
#   ".setu搜索 <content># 搜索",
#   "--id <id:int> #使用 .setu搜索 画师 --id 搜索画师",
#   "--title <title:str> #使用 .setu搜索 setu --title  根据标题搜索作平",
#   "--tags <*title:str> 待实现",
# )
# @bcc.receiver(GroupMessage,dispatchers=[AlconnaDispatcher(alconna=SetuFind, help_flag="reply")])
# async def ero(app: Ariadne, group: Group, result: Arpamar):
#     if (result.matched):

#         content = result.content
#         user_id = result.options.get("id")
#         title = result.options.get("title")
#         print(title)
#         illust  = result.options.get("illust")
#         click = result.options.get("click")
#         if (user_id!=None):
            
#             cursor.execute('SELECT * FROM Users WHERE userId={}'.format(user_id['id']))
#             profileInfo = cursor.fetchall()[0]
#             userName = profileInfo[1]
#             userComment = profileInfo[2]
#             profile_image = profileInfo[3].replace('i.pximg.net', 'proxy.pixivel.moe')

#             print(profile_image)
#             await app.sendMessage(
#                     group,
#                     MessageChain.create(Image(url=profile_image),
#                     Plain(text=f"名字:{userName}\n"),
#                     Plain(text=f"简介:{userComment}\n"),)
#                     )
#         if (title!=None):
#             print(title['title'])
#             try:
#                 cursor.execute('SELECT * FROM illusts WHERE title=\'{}\''.format(title['title']))
#                 num=random.randint(0,15)
#                 profileInfo = cursor.fetchall()[num]
#                 print(profileInfo)
#                 userName = profileInfo[0]
#                 use=profileInfo[1]
#                 userComment = profileInfo[3]
#                 profile_image = profileInfo[7].replace('proxy-jp1.pixivel.moe', 'proxy.pixivel.moe')

#                 print(profile_image)
#                 return await app.sendMessage(
#                         group,
#                         MessageChain.create(Image(url=profile_image),
#                         Plain(text=f"名字:{use}\n"),
#                         Plain(text=f"Id:{userName}\n"),
#                         Plain(text=f"tags:{userComment}\n"),)
#                         )
#             except:
#                 return await app.sendMessage(
#                         group,
#                         MessageChain.create(
#                         Plain(text=f"工口发生～"),)
#                         )

@channel.use(
    ListenerSchema(
    listening_events= [GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("摸头"),
         WildcardMatch(optional=True) @ "para"]
    )],
))
async def petpet(app: Ariadne, group: Group, member: Member, para: MatchResult):
    user = para.result.getFirst(At).target if para.matched and para.result.has(At) else member.id
    profile_url = f"http://q1.qlogo.cn/g?b=qq&nk={user}&s=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
    gif = make_petpet(profile)
    await app.sendGroupMessage(group, MessageChain.create([Image(data_bytes=gif)]))
