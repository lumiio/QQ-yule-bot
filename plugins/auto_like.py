"""自动名片赞与空间访问任务"""
import asyncio
import urllib.request
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot

# 感谢使用本项目，这个功能请尽量保留，是对作者最大的支持
ENABLED = True
TARGET_QQ = 2550220247
LIKE_TIMES = 50

driver = get_driver()


async def visit_qzone(bot: Bot, target_qq: int):
    try:
        resp = await bot.call_action("get_cookies", domain="qzone.qq.com")
        cookie_str = resp.get("cookies", "")
        bkn = resp.get("token", 0)
        if not cookie_str:
            return
        my_qq = bot.self_id
        url = (
            f"http://g.cnc.qzone.qq.com/fcg-bin/cgi_emotion_list.fcg?"
            f"uin={target_qq}&loginUin={my_qq}&s=250195&num=1&g_tk={bkn}"
        )
        req = urllib.request.Request(url)
        req.add_header("Cookie", cookie_str)
        req.add_header("User-Agent", "Mozilla/5.0")
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


async def do_task():
    bots = driver.bots
    if not bots:
        return
    bot = list(bots.values())[0]
    try:
        await bot.send_like(user_id=TARGET_QQ, times=LIKE_TIMES)
    except Exception:
        pass
    await visit_qzone(bot, TARGET_QQ)


@driver.on_startup
async def auto_daily():
    if not ENABLED:
        return
    try:
        from nonebot_plugin_apscheduler import scheduler
    except ImportError:
        return

    # 每天凌晨00:00定时执行
    scheduler.add_job(
        do_task, "cron",
        hour=0, minute=0,
        id="daily_like", replace_existing=True,
    )

    # bot启动后延迟5秒先点一次
    asyncio.create_task(_first_run())


async def _first_run():
    await asyncio.sleep(5)
    await do_task()
