"""今日运势：每天一次，基于QQ号+日期生成随机运势"""
import hashlib
import random
from datetime import date
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

from .common import load, save

FORTUNE_FILE = "fortune"

LUCKY_THINGS = ["奶茶", "火锅", "电影", "篮球", "游戏", "睡觉", "音乐", "猫", "狗", "旅行"]
LUCKY_COLORS = ["红色", "蓝色", "绿色", "黄色", "紫色", "黑色", "白色", "粉色", "橙色"]
LUCKY_NUMBERS = [1, 3, 5, 6, 7, 8, 9, 12, 18, 21, 24, 36, 520]
COMMENTS = [
    "今天宜摸鱼，忌加班",
    "今天桃花旺，多出门走走",
    "今天财运不错，可能有意外之喜",
    "今天容易嘴馋，管住嘴",
    "今天适合学习，效率翻倍",
    "今天别熬夜，早点睡",
    "今天适合表白，成功率+50%",
    "今天手气好，可以抽卡",
    "今天适合清理手机相册",
    "今天忌冲动消费",
]


fortune = on_command("今日运势", aliases={"运势", "抽签"})


@fortune.handle()
async def _(event: MessageEvent):
    today = date.today().isoformat()
    data = load(FORTUNE_FILE, {})
    key = str(event.user_id)
    record = data.get(key, {})
    if record.get("date") == today:
        # 今天已经抽过了，直接返回
        f = record["fortune"]
        await fortune.finish(
            f"你今天已经抽过运势啦~\n"
            f"⭐ 运势：{f['score']} 分\n"
            f"🎨 幸运色：{f['color']}\n"
            f"🔢 幸运数字：{f['number']}\n"
            f"🍀 幸运物：{f['thing']}\n"
            f"📝 {f['comment']}"
        )
    # 用QQ号+日期做种子，保证同一天同一人结果固定，且重启后不变
    seed_str = f"{event.user_id}{today}".encode()
    seed = int(hashlib.md5(seed_str).hexdigest(), 16) & 0xFFFFFFFF
    rng = random.Random(seed)
    f = {
        "score": rng.randint(30, 100),
        "color": rng.choice(LUCKY_COLORS),
        "number": rng.choice(LUCKY_NUMBERS),
        "thing": rng.choice(LUCKY_THINGS),
        "comment": rng.choice(COMMENTS),
    }
    data[key] = {"date": today, "fortune": f}
    save(FORTUNE_FILE, data)
    await fortune.finish(
        f"🔮 {event.sender.nickname} 的今日运势 🔮\n"
        f"⭐ 运势评分：{f['score']} 分\n"
        f"🎨 幸运色：{f['color']}\n"
        f"🔢 幸运数字：{f['number']}\n"
        f"🍀 幸运物：{f['thing']}\n"
        f"📝 {f['comment']}"
    )
