"""Emoji猜谜：bot发emoji串，群友抢答"""
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg
from .common import GameState
from .score import add_score

PUZZLES = [
    ("🐱🚪👨‍👩‍👧", "阖家欢乐"),
    ("🍎✈️", "平安夜"),
    ("🐑💉", "阳了"),
    ("🔥🐦", "凤凰"),
    ("🐘🐜", "大惊小怪"),
    ("❤️💣", "惊心动魄"),
    ("🐔🐶", "鸡犬不宁"),
    ("🌊🔥", "水火不容"),
    ("⭐🌙", "披星戴月"),
    ("🐉🐯", "龙争虎斗"),
    ("🌸💧", "落花流水"),
    ("👨‍💻☕", "程序员日常"),
    ("📱🔋", "手机没电"),
    ("🛏️📱", "睡前刷手机"),
    ("💰🌧️", "挥金如土"),
    ("🚪👃", "闻风丧胆"),
    ("🌙🌂", "阴雨天"),
    ("👀🚪", "望门"),
]

games = GameState()

start = on_command("emoji猜谜", aliases={"猜emoji", "emoji"})


@start.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if g and g["active"]:
        await start.finish("正在猜呢！输入 #答案 你的猜测")
    emoji, answer = random.choice(PUZZLES)
    games[gid] = {"emoji": emoji, "answer": answer, "active": True}
    await start.finish(f"🧩 看图猜谜！\n{emoji}\n\n输入 #答案 你的猜测")


guess = on_command("答案")


@guess.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = event.group_id
    g = games.get(gid)
    if not g or not g["active"]:
        await guess.finish("先输入 #emoji猜谜 开一局")
    guess_text = args.extract_plain_text().strip()
    if not guess_text:
        await guess.finish("你猜什么？比如 #答案 平安夜")
    answer = g["answer"]
    # 必须完整答案命中，或者答案的核心词（去掉常见后缀）在猜测里
    core = answer.rstrip("了吧呢啊的")
    if guess_text == answer or (len(core) >= 2 and core in guess_text):
        add_score(event.user_id, 2, event.sender.nickname or "")
        g["active"] = False
        await guess.finish(f"✅ {event.sender.nickname} 猜对了！答案：{answer}\n+2分")
    else:
        await guess.finish(f"❌ {guess_text} 不对哦，再想想~")

reveal = on_command("emoji答案", aliases={"揭谜"})


@reveal.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if not g or not g["active"]:
        await reveal.finish("没在猜")
    a = g["answer"]
    g["active"] = False
    await reveal.finish(f"🔑 答案：{a}")
