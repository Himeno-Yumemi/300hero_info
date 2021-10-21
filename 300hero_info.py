from urllib.parse import quote
from json import load, dump
from asyncio import Lock
from os.path import dirname, join, exists
from hoshino import Service,priv
from hoshino.util import FreqLimiter
from aiohttp import ClientSession
import nest_asyncio
nest_asyncio.apply()

sv_help = '''
【300英雄战绩查询功能指令】
-[绑定用户XXX]  绑定300英雄游戏内角色ID
-[用户信息]  查询自己的用户信息，可用@查询他人的信息
-[删除用户]  删除自己的用户信息，管理员可用@删除他人信息
-[团分] 查询自己的团分信息，可用@或指定ID获取他人信息
-[战场对局]  查询自己的战场对局信息，用@可以查询他人的信息
-[竞技场对局]  查询自己的竞技场对局信息，用@可以查询他人的信息
'''.strip()

sv = Service(
    name = '300英雄战绩',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )
@sv.on_fullmatch(["战绩帮助"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

lmt = FreqLimiter(5)
curpath = dirname(__file__)
config = join(curpath, '300hero_user.json')
root = {
    'group_bind' : {}
}
lck = Lock()
if exists(config):
    with open(config,encoding='UTF-8') as fp:
        root = load(fp)
binds = root['group_bind']

def save_binds():
    with open(config,'w',encoding='UTF-8') as fp:
        dump(root,fp,indent=4,ensure_ascii=False)

async def getjson(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            response = await response.json(content_type=None)
            return response

@sv.on_prefix(('绑定用户'))
async def bind_user(bot, ev):
    global binds,lck
    async with lck:
        uid = str(ev['user_id'])
        user=ev.message.extract_plain_text()
        binds[uid] = {
            'id': user
        }
        save_binds()
    await bot.finish(ev, f'\n角色：{user}\n绑定成功！', at_sender=True)

@sv.on_prefix('删除用户')
async def delete_user(bot,ev):
    global binds, lck
    uid = str(ev['user_id'])
    if ev.message[0].type == 'at':
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.finish(ev, '删除他人绑定请联系维护', at_sender=True)
            return
        uid = str(ev.message[0].data['qq'])
    elif len(ev.message) == 1 and ev.message[0].type == 'text' and not ev.message[0].data['text']:
        uid = str(ev['user_id'])
    if not uid in binds:
        await bot.finish(ev, '未绑定用户', at_sender=True)
        return
    async with lck:
        binds.pop(uid)
        save_binds()
    await bot.finish(ev, '删除用户绑定成功', at_sender=True)

@sv.on_prefix('用户信息')
async def bind_state(bot,ev):
    global binds, lck
    uid = str(ev['user_id'])
    if ev.message[0].type == 'at':
        id = str(ev.message[0].data['qq'])
        if not id in binds:
            await bot.send(ev,'对方还未绑定角色！', at_sender=True)
        else:
            info = binds[id]
            await bot.finish(ev,f"对方绑定信息：\n角色：{info['id']}",at_sender=True)
    else:
        if not uid in binds:
            await bot.send(ev,'您还未绑定角色！', at_sender=True)
        else:
            info = binds[uid]
            await bot.finish(ev,f"当前绑定信息：\n角色：{info['id']}",at_sender=True)

#用户id获取
async def user_get(ev):
    uid = str(ev['user_id'])
    key=ev.message.extract_plain_text()
    try:
        id=binds[uid]["id"]
        if key == "":
            key=binds[uid]["id"]
            return key
        else:
            return key
    except:
        return key


@sv.on_prefix(('团分'))
async def rank_score(bot, ev):
    if ev.message[0].type == 'at':
        id = str(ev.message[0].data['qq'])
        print(id)
        try:
            key=binds[id]["id"]
        except:
            msg = "对方未绑定用户，无法查询其信息！"
            await bot.send(ev, msg,at_sender=True)
            return
    else:
        key = await user_get(ev)
        if key == "":
            msg = "未绑定用户，请绑定用户或者指定用户名！"
            await bot.send(ev, msg,at_sender=True)
            return
    try:
        url='https://300report.jumpw.com/api/getrole?name={}'.format(quote(key))
        data=await getjson(url)
        #团分
        Rank=data["Rank"]
        for item in Rank:
            if item["RankName"]=="团队实力排行":
                Rank_Value=item["Value"]
                Rank_Rank=item["Rank"]
        #胜率
        Role=data["Role"]
        WinCount=Role["WinCount"]
        MatchCount=Role["MatchCount"]
        Winrate='{:.2f}%'.format(WinCount/MatchCount*100)
        #更新时间
        UpdateTime=Role["UpdateTime"]

        msg = f'\n用户名：{key}\n团分：{Rank_Value}\n排行：{Rank_Rank}\n胜率：{Winrate}\n更新时间：{UpdateTime}'
    except Exception as e:
        print(e)
        msg='\n查询不到该角色信息，可能是近期未进行过对局！'
    await bot.send(ev, msg,at_sender=True)

async def xinxi(key,judge,user_name,uid):
    try:
        url='https://300report.jumpw.com/api/getmatch?id={}'.format(key)
        data=await getjson(url)
        WinSide=data["Match"]["WinSide"]
        LoseSide=data["Match"]["LoseSide"]
        cord=""
        if judge == 1:
            for item in WinSide:
                if item["RoleName"]==user_name:
                    KillCount=item["KillCount"]
                    DeathCount=item["DeathCount"]
                    AssistCount=item["AssistCount"]
                    KillUnitCount=item["KillUnitCount"]
                    TotalMoney=item["TotalMoney"]
                    cord=f'{KillCount}/{DeathCount}/{AssistCount}/{KillUnitCount}/{TotalMoney}'
        elif judge == 2:
            for item in LoseSide:
                if item["RoleName"]==user_name:
                    KillCount=item["KillCount"]
                    DeathCount=item["DeathCount"]
                    AssistCount=item["AssistCount"]
                    KillUnitCount=item["KillUnitCount"]
                    TotalMoney=item["TotalMoney"]
                    cord=f'{KillCount}/{DeathCount}/{AssistCount}'
        else:
            for item in WinSide:
                if item["RoleName"]==user_name:
                    KillCount=item["KillCount"]
                    DeathCount=item["DeathCount"]
                    AssistCount=item["AssistCount"]
                    KillUnitCount=item["KillUnitCount"]
                    TotalMoney=item["TotalMoney"]
            for item in LoseSide:
                if item["RoleName"]==user_name:
                    KillCount=item["KillCount"]
                    DeathCount=item["DeathCount"]
                    AssistCount=item["AssistCount"]
                    KillUnitCount=item["KillUnitCount"]
                    TotalMoney=item["TotalMoney"]
            cord=f'{KillCount}/{DeathCount}/{AssistCount}/{KillUnitCount}/{TotalMoney}'
    except Exception as e:
        print(e)
    return cord

@sv.on_prefix(('战场对局','zc对局'))
async def battlefield_game(bot, ev):
    uid = str(ev['user_id'])
    if ev.message[0].type == 'at':
        id = str(ev.message[0].data['qq'])
        print(id)
        try:
            key=binds[id]["id"]
        except:
            msg = "对方未绑定用户，无法查询其信息！"
            await bot.send(ev, msg,at_sender=True)
            return
    else:
        key = await user_get(ev)
        if key == "":
            msg = "未绑定用户，请绑定用户或者指定用户名"
            await bot.send(ev, msg,at_sender=True)
            return
    if not lmt.check(uid):
        await bot.finish(ev, f'对局信息获取冷却中(剩余 {int(lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    lmt.start_cd(uid, 30)
    try:
        url='https://300report.jumpw.com/api/getlist?name={}'.format(quote(key))
        data=await getjson(url)
        List=data["List"]
        msg=f'\n用户名：{key}\n战场战绩:'
        for item in List:
            MatchID=item["MatchID"]
            MatchType=item["MatchType"]
            Result=item["Result"]
            Judge=item["Result"]
            Hero=item["Hero"]["Name"]
            if MatchType != 2:
                continue
            if Result == 1:
                Result="[CQ:face,id=175]"
            elif Result == 2:
                Result="[CQ:face,id=177]"
            else:
                Result="[CQ:face,id=37]"
            Record=await xinxi(MatchID,Judge,key,uid)
            if Record == "":
                continue
            msg += f'\n【{Result}{Hero}】{Record}'
    except Exception as e:
        print(e)
        msg='\n查询不到该角色信息，可能是近期未进行过对局！'
    await bot.send(ev, msg,at_sender=True)

@sv.on_prefix(('竞技场对局','jjc对局'))
async def arena_game(bot, ev):
    uid = str(ev['user_id'])
    #判断消息类型
    if ev.message[0].type == 'at':
        id = str(ev.message[0].data['qq'])
        print(id)
        try:
            key=binds[id]["id"]
        except:
            msg = "对方未绑定用户，无法查询其信息！"
            await bot.send(ev, msg,at_sender=True)
            return
    else:
        key = await user_get(ev)
        if key == "":
            msg = "未绑定用户，请绑定用户或者指定用户名"
            await bot.send(ev, msg,at_sender=True)
            return
    #进入cd
    if not lmt.check(uid):
        await bot.finish(ev, f'对局信息获取冷却中(剩余 {int(lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    lmt.start_cd(uid, 30)
    try:
        url='https://300report.jumpw.com/api/getlist?name={}'.format(quote(key))
        data=await getjson(url)
        List=data["List"]
        msg=f'\n用户名：{key}\n竞技场战绩:'
        for item in List:
            MatchID=item["MatchID"]
            MatchType=item["MatchType"]
            Result=item["Result"]
            Judge=item["Result"]
            Hero=item["Hero"]["Name"]
            if MatchType != 1:
                continue
            if Result == 1:
                Result="[CQ:face,id=175]"
            elif Result == 2:
                Result="[CQ:face,id=177]"
            else:
                Result="[CQ:face,id=37]"
            Record=await xinxi(MatchID,Judge,key,uid)
            if Record == "":
                continue
            msg += f'\n【{Result}{Hero}】{Record}'
    except Exception as e:
        print(e)
        msg='\n查询不到该角色信息，可能是近期未进行过对局！'
    await bot.send(ev, msg,at_sender=True)