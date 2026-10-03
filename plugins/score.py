"""积分系统：赢游戏加分，查看排行榜"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from .common import load, save

SCORE_FILE = "scores"


def get_score(user_id: int) -> int:
    data = load(SCORE_FILE, {})
    return data.get(str(user_id), {}).get("score", 0)


def add_score(user_id: int, delta: int, nickname: str = ""):
    data = load(SCORE_FILE, {})
    key = str(user_id)
    entry = data.get(key, {"score": 0, "name": ""})
    entry["score"] = entry.get("score", 0) + delta
    if nickname:
        entry["name"] = nickname
    data[key] = entry
    save(SCORE_FILE, data)


rank = on_command("排行", aliases={"排行榜", "scoreboard"})


@rank.handle()
async def _(event: GroupMessageEvent):
    data = load(SCORE_FILE, {})
    if not data:
        await rank.finish("还没有人积分，快来玩游戏上分吧！")
    sorted_items = sorted(data.items(), key=lambda x: x[1].get("score", 0), reverse=True)[:10]
    lines = ["🏆 群友积分榜 TOP10 🏆"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, info) in enumerate(sorted_items):
        name = info.get("name") or uid
        score = info.get("score", 0)
        prefix = medals[i] if i < 3 else f"  {i+1}."
        lines.append(f"{prefix} {name}：{score} 分")
    await rank.finish("\n".join(lines))


my_score = on_command("积分", aliases={"我的积分"})


@my_score.handle()
async def _(event: MessageEvent):
    s = get_score(event.user_id)
    # 顺便更新昵称
    add_score(event.user_id, 0, event.sender.nickname or "")
    await my_score.finish(f"你当前有 {s} 积分 🪙")
