"""公共工具：JSON 读写 + 带过期时间的游戏状态管理"""
import json
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 游戏状态存活时间：30 分钟无活动自动清理，防止内存泄漏
GAME_TTL = 30 * 60


def _path(name: str) -> Path:
    return DATA_DIR / f"{name}.json"


def load(name: str, default):
    p = _path(name)
    if not p.exists():
        return default
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(name: str, data):
    p = _path(name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class GameState:
    """按群隔离的游戏状态字典，自动清理超过 TTL 没动过的群。

    用法：
        games = GameState()
        games[gid] = {...}        # 写入
        g = games.get(gid)        # 读取（自动丢弃过期项）
        if gid in games:          # 判断（自动清理过期项）
    """

    def __init__(self, ttl: int = GAME_TTL):
        self._data = {}
        self._ttl = ttl

    def _purge(self, now: float):
        expired = [k for k, v in self._data.items() if now - v["_ts"] > self._ttl]
        for k in expired:
            del self._data[k]

    def __setitem__(self, key, value):
        self._data[key] = {"_ts": time.time(), "data": value}

    def get(self, key, default=None):
        now = time.time()
        self._purge(now)
        item = self._data.get(key)
        if item is None:
            return default
        item["_ts"] = now  # 续命
        return item["data"]

    def __contains__(self, key):
        now = time.time()
        self._purge(now)
        return key in self._data

    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]

    def pop(self, key, default=None):
        now = time.time()
        self._purge(now)
        item = self._data.pop(key, None)
        return item["data"] if item else default
