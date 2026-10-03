"""谁是卧底：群里4-8人玩，bot当法官私聊发词"""
import random
from collections import Counter
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from .common import GameState

WORDS = [
    ("牛奶", "豆浆"), ("披萨", "馅饼"), ("苹果", "梨"),
    ("篮球", "排球"), ("微信", "QQ"), ("奶茶", "咖啡"),
    ("饺子", "包子"), ("蜘蛛侠", "蝙蝠侠"), ("熊猫", "考拉"),
    ("火锅", "麻辣烫"), ("口红", "唇膏"), ("墨镜", "眼镜"),
    ("雨伞", "雨衣"), ("自行车", "电动车"), ("微博", "朋友圈"),
    ("西瓜", "冬瓜"), ("猫", "狗"), ("可乐", "雪碧"),
    ("春节", "元旦"), ("爸爸", "叔叔"), ("裙子", "裤子"),
    ("薯条", "薯片"), ("蜡烛", "灯泡"), ("枕头", "抱枕"),
    ("洗发水", "沐浴露"), ("牙刷", "筷子"), ("电梯", "楼梯"),
    ("矿泉水", "蒸馏水"), ("钢琴", "电子琴"),
]

games = GameState()

start = on_command("卧底开局", aliases={"谁是卧底"})


@start.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if g and g["phase"] != "idle":
        await start.finish("这局还没结束呢！")
    games[gid] = {
        "phase": "waiting", "players": [event.user_id],
        "words": {}, "undercover": None, "alive": [],
    }
    await start.finish(
        f"🎮 谁是卧底开局！\n发起人：{event.sender.nickname}\n"
        f"输入 #加入 报名（4-8人），人齐后输入 #发词"
    )


join = on_command("卧底加入", aliases={"加入"})


@join.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if not g or g["phase"] != "waiting":
        await join.finish("现在没在招人哦")
    if event.user_id in g["players"]:
        await join.finish("你已经在里面了")
    if len(g["players"]) >= 8:
        await join.finish("人满了！")
    g["players"].append(event.user_id)
    await join.finish(f"✅ {event.sender.nickname} 加入了！当前 {len(g['players'])} 人")


deal = on_command("开始发词", aliases={"发词"})


@deal.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    gid = event.group_id
    g = games.get(gid)
    if not g or g["phase"] != "waiting":
        await deal.finish("还没开局或已经开始了")
    if len(g["players"]) < 4:
        await deal.finish(f"人太少了（现在{len(g['players'])}人），至少4人才能开局")
    civilian_word, undercover_word = random.choice(WORDS)
    undercover = random.choice(g["players"])
    g["undercover"] = undercover
    g["alive"] = list(g["players"])
    for uid in g["players"]:
        g["words"][uid] = undercover_word if uid == undercover else civilian_word
    failed = []
    for uid, word in g["words"].items():
        try:
            await bot.send_private_msg(user_id=uid, message=f"🎭 你的词是：{word}\n（记住别告诉别人）")
        except Exception:
            failed.append(uid)
    g["phase"] = "describing"
    msg = "📨 词已经私聊发给每个人了！\n请大家轮流描述自己的词，然后输入 #投票 @某人 开始放逐"
    if failed:
        at_list = " ".join([f"[CQ:at,qq={uid}]" for uid in failed])
        msg += (
            f"\n\n⚠️ {at_list}\n"
            f"你们没开私聊，bot发不了词！\n"
            f"请先随便给bot发条私信，然后让管理员重新 #发词"
        )
    await deal.finish(msg)


vote = on_command("卧底投票", aliases={"投票"})


@vote.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if not g or g["phase"] != "describing":
        await vote.finish("现在不是投票阶段")
    msg = event.get_message()
    target = None
    for seg in msg:
        if seg.type == "at":
            target = int(seg.data["qq"])
            break
    if target is None:
        await vote.finish("请 @你要投的人，比如 #投票 @某某")
    if target not in g["alive"]:
        await vote.finish("这个人不在场上")
    if "votes" not in g:
        g["votes"] = {}
    g["votes"][event.user_id] = target

    alive_set = set(g["alive"])
    voted_set = set(g["votes"].keys())
    if not alive_set.issubset(voted_set):
        wait = len(alive_set - voted_set)
        await vote.finish(f"✅ 你已投票，等待 {wait} 人投票...")

    counter = Counter(g["votes"].values())
    g["votes"] = {}
    top = counter.most_common(2)
    if len(top) == 2 and top[0][1] == top[1][1]:
        await vote.finish(f"🤝 平票！{top[0][0]} 和 {top[1][0]} 都是 {top[0][1]} 票，重新投票！")
        return
    voted_out = top[0][0]
    g["alive"].remove(voted_out)
    is_undercover = voted_out == g["undercover"]

    if is_undercover:
        uw_word = g["words"][g["undercover"]]
        del games[gid]
        await vote.finish(
            f"🗳️ 投票：{dict(counter)}\n❌ {voted_out} 被放逐！\n"
            f"🎉 他就是卧底！平民胜利！卧底词：{uw_word}"
        )
    elif len(g["alive"]) <= 2:
        uw = g["undercover"]
        uw_word = g["words"][uw]
        del games[gid]
        await vote.finish(
            f"🗳️ 投票：{dict(counter)}\n❌ {voted_out} 被放逐，不是卧底...\n"
            f"😱 只剩 {len(g['alive'])} 人！卧底胜利！卧底是 {uw}，词：{uw_word}"
        )
    else:
        await vote.finish(
            f"🗳️ 投票：{dict(counter)}\n❌ {voted_out} 被放逐，不是卧底...\n"
            f"还剩 {len(g['alive'])} 人，继续 #投票"
        )


quit_game = on_command("卧底退出")


@quit_game.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    games.pop(gid)
    await quit_game.finish("本局已结束")
