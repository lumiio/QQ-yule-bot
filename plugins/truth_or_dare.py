"""真心话大冒险"""
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .truth_or_dare_data import TRUTH, DARE

truth = on_command("真心话")
dare = on_command("大冒险")


@truth.handle()
async def _(event: GroupMessageEvent):
    q = random.choice(TRUTH)
    await truth.finish(f"🙈 真心话：{q}")


@dare.handle()
async def _(event: GroupMessageEvent):
    q = random.choice(DARE)
    await dare.finish(f"😈 大冒险：{q}")
