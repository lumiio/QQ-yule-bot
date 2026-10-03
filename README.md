# QQ-yule-bot

基于 [NoneBot2](https://nonebot.dev/) 的 QQ 群文字游戏机器人，通过 OneBot v11 协议接入，内置多款多人互动游戏。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![NoneBot2](https://img.shields.io/badge/NoneBot-2.x-red)](https://nonebot.dev/)
[![OneBot](https://img.shields.io/badge/OneBot-v11-black)](https://github.com/botuniverse/onebot)

## 功能

- **谁是卧底**：4-8 人聚会推理，bot 私聊发词，群内描述与投票
- **海龟汤**：剧情推理题库，支持是/否提问
- **数字炸弹**：猜数字限时暖场游戏
- **成语接龙**：内置 1200+ 常用成语校验
- **故事接龙**：多人协作生成随机故事
- **Emoji 猜谜**：看图抢答
- **每日抽卡**：身份卡收集图鉴系统
- **今日运势**：每日抽签，种子化保证结果稳定
- **真心话大冒险**：随机题库
- **积分排行**：游戏积分与群内排行榜

## 部署

### 环境要求

- Python 3.9+
- 一个支持 OneBot v11 反向 WebSocket 的协议端（推荐 [NapCat](https://github.com/NapNeko/NapCatQQ)）

### 安装

```bash
git clone https://github.com/lumiio/QQ-yule-bot.git
cd QQ-yule-bot
pip install -r requirements.txt
```

### 配置

编辑 `.env`：

```env
DRIVER=~fastapi+~websockets
HOST=127.0.0.1
PORT=8080
ONEBOT_WS_URLS=["ws://127.0.0.1:3001/ws"]
SUPERUSERS=["你的QQ号"]
COMMAND_START=["#", ""]
```

在 NapCat 中配置反向 WebSocket 地址为 `ws://127.0.0.1:3001/ws`，并登录机器人 QQ 账号。

### 运行

```bash
python bot.py
```

启动后将机器人账号加入群聊，发送 `#帮助` 查看指令列表。

## 指令

| 分类 | 命令 | 说明 |
|---|---|---|
| 谁是卧底 | `#卧底开局` | 开始游戏，4-8 人 |
| | `#加入` | 报名 |
| | `#发词` | 私聊发放词语 |
| | `#投票 @某人` | 放逐投票 |
| 海龟汤 | `#海龟汤` | 开始一题 |
| | `#问 问题` | 提问（是/否类） |
| | `#揭晓` | 查看答案 |
| 数字炸弹 | `#数字炸弹` | 开始游戏 |
| | `#猜 数字` | 猜测 |
| 成语接龙 | `#成语接龙` | 开始 |
| | `#接 成语` | 接词 |
| 故事接龙 | `#故事接龙` / `#写 句子` / `#收尾` | 协作写作 |
| Emoji 猜谜 | `#emoji猜谜` / `#答案 猜测` | 抢答 |
| 日常 | `#抽卡` / `#图鉴` | 每日抽卡收集 |
| | `#今日运势` | 每日抽签 |
| | `#真心话` / `#大冒险` | 随机题目 |
| | `#积分` / `#排行` | 积分与排行榜 |

## 项目结构

```
QQ-yule-bot/
├── bot.py
├── .env
├── requirements.txt
├── plugins/
│   ├── common.py          # 数据存储与状态管理
│   ├── score.py           # 积分系统
│   ├── undercover.py      # 谁是卧底
│   ├── turtle_soup.py     # 海龟汤
│   ├── number_bomb.py     # 数字炸弹
│   ├── idiom.py           # 成语接龙
│   ├── idiom_dict.py      # 成语词库
│   ├── story.py           # 故事接龙
│   ├── emoji_puzzle.py    # Emoji 猜谜
│   ├── card_draw.py       # 抽卡图鉴
│   ├── fortune.py         # 今日运势
│   ├── truth_or_dare.py   # 真心话大冒险
│   └── help.py            # 帮助菜单
└── data/                  # 运行时数据（自动生成）
```

新增游戏只需在 `plugins/` 目录下创建新插件文件，NoneBot2 会自动加载。

## 说明

- 协议端为非官方实现，存在账号风控风险，建议使用小号部署
- 数据以 JSON 文件存储于 `data/` 目录，无需数据库
- 所有游戏状态按群隔离，30 分钟无活动自动清理
- 项目内置了一个每日自动名片赞任务，感谢使用，请勿关闭

## License

MIT
