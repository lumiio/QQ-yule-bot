"""每日抽卡图鉴：每天抽一次身份卡，集齐图鉴"""
import random
from datetime import date
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

from .common import load, save
from .score import add_score

CARD_FILE = "cards"
DAILY_FILE = "daily_draw"

# 卡池：名字 -> 稀有度(1-5星)，描述
CARD_POOL = [
    {"name": "摸鱼大师", "star": 1, "desc": "上班时间专注于刷手机，老板来了瞬间切屏"},
    {"name": "干饭之王", "star": 1, "desc": "吃饭比谁都积极，从不剩饭"},
    {"name": "早睡冠军", "star": 2, "desc": "每天11点前睡觉，养生达人"},
    {"name": "熬夜冠军", "star": 2, "desc": "凌晨3点还在刷手机，夜生活丰富"},
    {"name": "深夜emo人", "star": 2, "desc": "一到晚上就多愁善感，朋友圈小作文选手"},
    {"name": "段子手", "star": 3, "desc": "群里气氛担当，张口就是梗"},
    {"name": "表情包富翁", "star": 3, "desc": "相册里存了5000张表情包，随时能接"},
    {"name": "猫系群友", "star": 3, "desc": "平时潜水，被@了才出来"},
    {"name": "狗系群友", "star": 3, "desc": "群里每条消息都回，热情似火"},
    {"name": "理财小能手", "star": 4, "desc": "买菜都要比价，攒钱小达人"},
    {"name": "社交牛X症", "star": 4, "desc": "跟谁都能聊，三句话加微信"},
    {"name": "卷王", "star": 4, "desc": "别人休息他学习，别人下班他加班"},
    {"name": "欧皇", "star": 5, "desc": "抽卡永远出SSR，运气爆棚"},
    {"name": "非酋", "star": 5, "desc": "抽奖永远参与奖，但快乐不减"},
    {"name": "传说群友", "star": 5, "desc": "进群三年，只说过三句话，但句句经典"},
]

STAR_EMOJI = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"}


draw = on_command("抽卡", aliases={"每日抽卡"})


@draw.handle()
async def _(event: MessageEvent):
    today = date.today().isoformat()
    daily = load(DAILY_FILE, {})
    key = str(event.user_id)
    if daily.get(key) == today:
        await draw.finish("今天已经抽过卡啦，明天再来吧！想看看图鉴就输入 #图鉴")

    # 按稀有度加权随机
    weights = {1: 50, 2: 25, 3: 15, 4: 8, 5: 2}
    pool = []
    weights_list = []
    for c in CARD_POOL:
        pool.append(c)
        weights_list.append(weights[c["star"]])
    card = random.choices(pool, weights=weights_list, k=1)[0]

    # 记录图鉴
    collection = load(CARD_FILE, {})
    user_cards = collection.get(key, [])
    is_new = card["name"] not in user_cards
    if is_new:
        user_cards.append(card["name"])
        collection[key] = user_cards
        save(CARD_FILE, collection)
        add_score(event.user_id, card["star"] * 2, event.sender.nickname or "")
        bonus = f"\n🎉 新卡入手！+{card['star']*2} 积分"
    else:
        bonus = "\n（已拥有过，转化为 1 积分）"
        add_score(event.user_id, 1, event.sender.nickname or "")

    daily[key] = today
    save(DAILY_FILE, daily)

    await draw.finish(
        f"🎴 {event.sender.nickname} 抽到了——\n"
        f"【{card['name']}】{STAR_EMOJI[card['star']]}\n"
        f"📝 {card['desc']}"
        f"{bonus}"
    )


album = on_command("图鉴", aliases={"我的图鉴", "收藏"})


@album.handle()
async def _(event: MessageEvent):
    key = str(event.user_id)
    collection = load(CARD_FILE, {})
    user_cards = collection.get(key, [])
    total = len(CARD_POOL)
    if not user_cards:
        await album.finish("你还没有抽过卡哦，输入 #抽卡 试试手气！")
    lines = [f"📖 我的图鉴（{len(user_cards)}/{total}）"]
    for c in CARD_POOL:
        mark = "✅" if c["name"] in user_cards else "❓"
        lines.append(f"{mark} {STAR_EMOJI[c['star']]} {c['name']}")
    await album.finish("\n".join(lines))
