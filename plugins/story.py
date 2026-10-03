"""故事接龙：bot起头，群友一人一句"""
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from .common import GameState

STARTERS = [
    "那天晚上，我收到了一条陌生短信：",
    "世界上最后一个人坐在房间里，突然响起了敲门声。",
    "我在古董市场买到一面镜子，回家后发现——",
    "2045年，我终于发明了时光机，第一个想去的是——",
    "公司年会上，老板抽中了特等奖，打开信封后脸色大变。",
    "我搬进新家的第一晚，发现墙里传来轻微的敲击声。",
]

games = GameState()

start = on_command("故事接龙", aliases={"写故事"})


@start.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    if games.get(gid):
        await start.finish("故事正在写呢，输入 #写 你的句子 继续！")
    starter = random.choice(STARTERS)
    games[gid] = {"lines": [(event.user_id, event.sender.nickname, starter)]}
    await start.finish(f"📝 故事开始了！\n「{starter}」\n\n输入 #写 你接的句子，写几段后 #收尾")


write = on_command("写")


@write.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = event.group_id
    g = games.get(gid)
    if not g:
        await write.finish("先输入 #故事接龙 开始吧！")
    text = args.extract_plain_text().strip()
    if not text:
        await write.finish("你要写什么？比如 #写 我打开门，发现是一只会说话的猫。")
    g["lines"].append((event.user_id, event.sender.nickname, text))
    n = len(g["lines"])
    await write.finish(f"✅ 第{n}句已记录（{event.sender.nickname}）\n继续 #写，或输入 #收尾 看完整故事")


finish = on_command("收尾", aliases={"写完", "结束故事"})


@finish.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.pop(gid)
    if not g:
        await finish.finish("没在写故事")
    story = "".join(text for _, _, text in g["lines"])
    authors = "、".join(dict.fromkeys(name for _, name, _ in g["lines"]))
    await finish.finish(f"📖 完整故事出炉！\n\n{story}\n\n—— 参与作者：{authors}")
