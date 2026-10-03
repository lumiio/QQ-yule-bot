"""数字炸弹：bot想一个数字，大家轮流猜，范围缩小，踩中者输"""
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from .common import GameState
from .score import add_score

games = GameState()

start = on_command("数字炸弹", aliases={"炸弹"})


@start.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = event.group_id
    if games.get(gid):
        await start.finish("本群已经有一局在进行了，输入 #猜 数字 来猜吧！")
    n = 100
    text = args.extract_plain_text().strip()
    if text.isdigit():
        n = int(text)
        if n < 10 or n > 1000:
            await start.finish("数字范围要在 10~1000 之间哦")
    target = random.randint(1, n)
    games[gid] = {"target": target, "low": 1, "high": n, "players": []}
    await start.finish(f"💣 数字炸弹开始！范围 1~{n}\n输入 #猜 数字 开始猜吧！")


guess = on_command("猜")


@guess.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = event.group_id
    g = games.get(gid)
    if not g:
        await guess.finish("还没开局呢，先输入 #数字炸弹 开始吧！")
    text = args.extract_plain_text().strip()
    if not text.lstrip("-").isdigit():
        await guess.finish("请输入数字，比如 #猜 50")
    num = int(text)
    if not (g["low"] <= num <= g["high"]):
        await guess.finish(f"范围是 {g['low']} ~ {g['high']}，别猜范围外的哦")

    g["players"].append((event.user_id, event.sender.nickname))

    if num == g["target"]:
        loser_name = event.sender.nickname or str(event.user_id)
        bonus_msg = ""
        # 找上一个不同的群友作为幸免者，避免同一个人连续猜时给自己加分
        for prev_uid, prev_name in reversed(g["players"][:-1]):
            if prev_uid != event.user_id:
                add_score(prev_uid, 2, prev_name)
                bonus_msg = f"\n🏅 幸免于难的 {prev_name} +2 分"
                break
        del games[gid]
        await guess.finish(f"💥 {loser_name} 踩到炸弹了！答案就是 {g['target']}{bonus_msg}")
    elif num < g["target"]:
        g["low"] = num + 1
    else:
        g["high"] = num - 1
    await guess.finish(f"📢 {event.sender.nickname} 猜了 {num}\n范围缩小到 {g['low']} ~ {g['high']}")
