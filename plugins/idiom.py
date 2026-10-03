"""成语接龙：bot起头，群友接成语，校验是否为真成语"""
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

from .common import GameState
from .idiom_dict import IDIOMPHS
from .score import add_score

START_WORDS = ["一马当先", "一心一意", "万事如意", "风和日丽", "一帆风顺"]

games = GameState()

jie_start = on_command("成语接龙", aliases={"接龙"})


@jie_start.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.get(gid)
    if g:
        await jie_start.finish(f"正在接呢！上一个成语结尾是「{g['last_word']}」，快接！")
    word = random.choice(START_WORDS)
    games[gid] = {"last_word": word[-1], "word": word}
    await jie_start.finish(
        f"📖 成语接龙开始！\nbot 起头：{word}\n"
        f"请接「{word[-1]}」开头的成语，格式 #接 成语"
    )


jie_answer = on_command("接")


@jie_answer.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = event.group_id
    g = games.get(gid)
    if not g:
        await jie_answer.finish("还没开局呢，先输入 #成语接龙")
    word = args.extract_plain_text().strip()
    if len(word) < 3:
        await jie_answer.finish("太短啦，至少要3个字的成语，比如 #接 先睹为快")
    last = g["last_word"]
    if word[0] != last:
        await jie_answer.finish(f"要接「{last}」开头哦，你接的是「{word[0]}」")
    # 校验是否为成语
    if word not in IDIOMPHS:
        await jie_answer.finish(
            f"「{word}」好像不是成语哦🤔\n"
            f"换一个正经的成语试试？（要接「{last}」开头）"
        )
    add_score(event.user_id, 2, event.sender.nickname or "")
    games[gid] = {"last_word": word[-1], "word": word}
    await jie_answer.finish(f"✅ {event.sender.nickname} 接了「{word}」+2分\n请继续接「{word[-1]}」开头的成语")


jie_stop = on_command("接龙结束")


@jie_stop.handle()
async def _(event: GroupMessageEvent):
    gid = event.group_id
    g = games.pop(gid)
    if not g:
        await jie_stop.finish("本来就没在玩")
    await jie_stop.finish(f"🏁 接龙结束！最后一个成语是「{g['word']}」")
