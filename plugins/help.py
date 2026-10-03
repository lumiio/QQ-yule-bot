"""帮助菜单"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

help_cmd = on_command("帮助", aliases={"菜单", "功能", "help"})


@help_cmd.handle()
async def _(event: MessageEvent):
    await help_cmd.finish(
        "🎮 群游戏 Bot 指令大全 🎮\n"
        "——————————————\n"
        "【聚会多人局】\n"
        "#卧底开局 → 谁是卧底（4-8人）\n"
        "#加入 → 报名卧底\n"
        "#发词 → bot私聊发词\n"
        "#投票 @某人 → 放逐\n"
        "#海龟汤 → 推理谜题\n"
        "#问 你的问题 → 海龟汤提问\n"
        "#揭晓 → 看海龟汤答案\n"
        "#故事接龙 → 群友一起写故事\n"
        "#写 句子 → 接一句\n"
        "#收尾 → 看完整故事\n"
        "——————————————\n"
        "【休闲小游戏】\n"
        "#数字炸弹 → 1~100猜数字\n"
        "#猜 50 → 猜炸弹\n"
        "#emoji猜谜 → emoji猜成语/电影\n"
        "#答案 猜测 → 答题\n"
        "#成语接龙 → 开始接龙\n"
        "#接 成语 → 接成语\n"
        "#真心话 → 抽一个\n"
        "#大冒险 → 抽一个\n"
        "——————————————\n"
        "【每日日常】\n"
        "#抽卡 → 每日抽身份卡\n"
        "#图鉴 → 查看收藏\n"
        "#今日运势 → 每日运势\n"
        "#积分 → 我的积分\n"
        "#排行 → 积分榜\n"
    )
