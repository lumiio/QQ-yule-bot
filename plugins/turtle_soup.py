"""海龟汤：预制题库，玩家提问，bot按关键词判断回答"""
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg
from .common import GameState
from .score import add_score

SOUPS = [
    {
        "surface": "一个男人走进酒吧要一杯水，酒保掏出枪指着他。男人说「谢谢」然后走了。为什么？",
        "answer": "男人在打嗝，想用水压一下。酒保掏枪吓他，打嗝好了，所以道谢离开。",
        "yes": ["打嗝", "饱", "吓", "枪", "谢谢", "走", "感谢", "水"],
        "no": ["死", "杀", "钱", "抢劫"],
    },
    {
        "surface": "女人穿黑色雨衣走在田野里，突然尖叫一声倒地身亡。为什么？",
        "answer": "雷雨天，她雨衣的金属拉链引雷被劈了。",
        "yes": ["雷", "雨", "闪电", "劈", "金属", "拉链", "天气", "电"],
        "no": ["谋杀", "人杀", "毒", "刀"],
    },
    {
        "surface": "小明住10楼，每天下班电梯只坐到7楼然后爬楼梯。但下雨或电梯有人时他直接到10楼。为什么？",
        "answer": "他是小孩/矮子，够不到10楼按钮。下雨有伞可以戳，有人可以帮忙按。",
        "yes": ["矮", "小", "够", "按钮", "身高", "伞", "帮忙", "别人"],
        "no": ["减肥", "锻炼", "生病"],
    },
    {
        "surface": "一个人半夜醒来，房间里灯突然亮了。他看了一眼窗外，立刻跳楼自杀了。为什么？",
        "answer": "他是灯塔看守人，醒来发现灯塔没亮，知道有船要出事，愧疚自杀。",
        "yes": ["灯塔", "船", "海", "灯", "值班", "工作", "愧疚"],
        "no": ["鬼", "仇人", "追杀"],
    },
    {
        "surface": "女人每天回家坐电梯到20楼，然后走楼梯到25楼。但下雨天她直接坐到25楼。为什么？",
        "answer": "她是侏儒，按不到25楼按钮，只能够到20楼。下雨天有伞可以用伞戳25楼按钮。",
        "yes": ["矮", "侏儒", "够", "按钮", "伞", "下雨天"],
        "no": ["减肥", "锻炼", "健身"],
    },
    {
        "surface": "男人打开冰箱门看了一眼，立刻关上并报了警。为什么？",
        "answer": "他在冰箱里发现了尸体/人头，知道家里进了凶手。",
        "yes": ["尸体", "人头", "藏", "发现", "血", "死"],
        "no": ["食物", "过期", "坏了"],
    },
    {
        "surface": "一个人在沙漠里死了，手里紧紧攥着半根火柴。周围没有脚印。为什么？",
        "answer": "他坐热气球超载，抽火柴决定谁跳下去，他抽到半根死了。",
        "yes": ["热气球", "球", "飞", "超载", "抽签", "火柴", "跳"],
        "no": ["迷路", "渴", "晒", "走"],
    },
    {
        "surface": "弟弟在姐姐葬礼上看到一个陌生男人，回家后把妹妹杀了。为什么？",
        "answer": "弟弟想再见到那个男人，所以再办一场葬礼。（经典海龟汤）",
        "yes": ["再见", "男人", "葬礼", "杀", "妹妹", "想见", "第二次"],
        "no": ["争遗产", "吵架", "矛盾"],
    },
]

games = GameState()

start = on_command("海龟汤", aliases={"来个汤"})


@start.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if g and g["active"]:
        await start.finish("这题还没猜完呢，继续问吧！输入 #提示 要提示")
    soup = random.choice(SOUPS)
    games[gid] = {"soup": soup, "active": True}
    await start.finish(f"🍲 海龟汤来了！\n{soup['surface']}\n\n输入 #问 你的问题（是/否类），输入 #揭晓 看答案")


ask = on_command("问")


@ask.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = event.group_id
    g = games.get(gid)
    if not g or not g["active"]:
        await ask.finish("先输入 #海龟汤 开一局吧！")
    q = args.extract_plain_text().strip()
    if not q:
        await ask.finish("你要问什么？比如 #问 他是被人杀的吗？")
    soup = g["soup"]
    if any(k in q for k in soup["no"]):
        result = "❌ 否"
    elif any(k in q for k in soup["yes"]):
        result = "✅ 是"
    else:
        result = "🤔 无关 / 不重要"
    await ask.finish(f"{event.sender.nickname}：{q}\n{result}")


reveal = on_command("揭晓")


@reveal.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if not g or not g["active"]:
        await reveal.finish("没在玩海龟汤")
    soup = g["soup"]
    g["active"] = False
    add_score(event.user_id, 3, event.sender.nickname or "")
    await reveal.finish(f"🔑 答案：{soup['answer']}\n\n👍 {event.sender.nickname} +3分\n输入 #海龟汤 再来一题")


hint = on_command("提示")


@hint.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if not g or not g["active"]:
        await hint.finish("没在玩海龟汤")
    await hint.finish("💡 提示：注意题目里反常的细节，往出人意料但合理的方向想。")
