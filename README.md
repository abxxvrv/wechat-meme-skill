# 微信表情包.skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-7c3aed?labelColor=4b5563)
![skills.sh Compatible](https://img.shields.io/badge/skills.sh-Compatible-76b900?labelColor=4b5563)
![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-f97316?labelColor=4b5563)

> 「别只会回复文字。让智能体也有表情。」

微信表情包.skill 是一个给智能体使用的本地表情包技能：  
当它想表达轻松、感性、可爱、安慰、接梗、破防、害羞、阴阳怪气时，不必硬写一句话，可以从语义索引里挑一个真正合适的表情包。

不是随机发表情。  
是把表情包变成一个可检索、可维护、可判断语境的情绪表达库。

[安装](#安装) · [效果示例](#效果示例) · [它解决什么](#它解决什么) · [工作原理](#工作原理) · [仓库结构](#仓库结构)

---

## 效果示例

```text
用户      ❯ 她说今天好累，想早点睡

Agent     ❯ 可以用这个：
           stickers/bear_pet_good_boy_01.mp4
           含义：乖喔，摸摸头安慰
```

```text
用户      ❯ 群里有人说“我又把生产环境搞炸了”，发个破防但好笑的

Agent     ❯ 可以用这个：
           stickers/duck_crying_guitar_01.mp4
           含义：一边哭一边唱，委屈但有节目效果
```

```text
用户      ❯ 把这个 GIF 加进表情包库

Agent     ❯ 已加入表情包库：

           id: awkward_polite_smile_01
           file: stickers/awkward_polite_smile_01.mp4
           含义: 尴尬而不失礼貌地笑
           适合: 轻松语境下缓和尴尬、接住玩笑
```

---

## 安装

```bash
npx skills add abxxvrv/wechat-meme-skill
```

也可以直接把本仓库放到你的 skills 目录中使用。

依赖：

```bash
pip install -r requirements.txt
```

如果需要把 GIF 转 MP4，请确保本机可用 `ffmpeg`。

---

## 它解决什么

很多聊天里的意思，不适合用一句正经文字表达：

- “哈哈哈笑死”
- “抱抱你”
- “我懂，我也破防了”
- “有点害羞但想接话”
- “轻轻阴阳一下”
- “用可爱方式说不知道”

这个 skill 让智能体先读 `index.yaml`，理解每个表情包的：

```text
它是什么意思
表达什么情绪
适合什么时候用
不适合什么时候用
表达强度有多高
文件在哪里
```

然后再选择最贴近当前聊天语气的图片或 MP4。

---

## 工作原理

1. 语义索引  
   `index.yaml` 记录每个表情包的含义、情绪、意图、语气、强度、适用场景和文件路径。

2. 情绪优先匹配  
   智能体不只看文件名，而是按 `short_meaning`、`emotion`、`intent`、`tone`、`tags` 来选择。

3. 只发送图片或 MP4  
   可发送文件只允许 `.jpg`、`.jpeg`、`.png`、`.webp`、`.mp4`。GIF 只作为输入格式。

4. GIF 自动转 MP4  
   用户提供 GIF 时，使用 `scripts/gif_to_mp4.py` 转成 1-2 秒 MP4。短 GIF 会完整循环多次，超过 2 秒的 GIF 会播放一次并轻微加速。

5. 可维护  
   新表情包可以用脚本生成 metadata、复制入库、更新索引、校验文件存在性。

---

## 常用命令

校验索引：

```bash
python scripts/validate_index.py --root .
```

选择表情包：

```bash
python scripts/select_sticker.py --root . --query "抱抱 安慰"
```

给 GIF 生成关键帧图，辅助理解动图含义：

```bash
python scripts/gif_contact_sheet.py path/to/input.gif sticker_sheets/input_sheet.jpg
```

把 GIF 转成 1-2 秒 MP4：

```bash
python scripts/gif_to_mp4.py path/to/input.gif --output-dir stickers --overwrite
```

生成 metadata 草稿：

```bash
python scripts/annotate_sticker.py path/to/input.gif --id awkward_polite_smile_01 --meaning "尴尬而不失礼貌地笑"
```

加入表情包库：

```bash
python scripts/add_sticker.py path/to/input.gif --root . --metadata path/to/metadata.yaml
```

如果输入是 GIF，`add_sticker.py` 会自动转换为同名 MP4 后写入索引。

---

## 仓库结构

```text
wechat-meme-skill/
├── SKILL.md                       # 技能本体：触发规则、选择流程、维护流程
├── index.yaml                     # 表情包语义索引
├── stickers/                      # 可发送表情文件：图片或 MP4
├── sticker_sheets/                # GIF 关键帧图，用于辅助标注
├── scripts/
│   ├── annotate_sticker.py        # 生成单个表情包 metadata 草稿
│   ├── add_sticker.py             # 复制/转换文件并更新 index.yaml
│   ├── gif_contact_sheet.py       # GIF 抽帧成九宫格/联系表
│   ├── gif_to_mp4.py              # GIF 转 1-2 秒 MP4
│   ├── select_sticker.py          # 按关键词从 index.yaml 检索表情
│   └── validate_index.py          # 校验索引和文件引用
└── requirements.txt
```

---

## 设计原则

### 表情包是语义表达库

它不是一个图片文件夹。  
对智能体来说，每个表情包都必须带着“什么时候用”和“怎么理解”的信息。

### 优先考虑轻松感性表达

当智能体想表达轻松、感性、可爱、安慰、接梗、玩梗等内容时，应该优先考虑这个 skill，而不是只输出文字。

### 但不要替代必要回应

表情包不能代替实际帮助、认真道歉、明确说明或技术排错。需要说清楚的时候，先说清楚。

---

## 当前内置表情

本仓库内置 20 个表情条目：

- 17 个 MP4 动态表情
- 3 个 JPG 静态表情

全部由 `index.yaml` 统一管理。

---

## 许可证

MIT — 随便用，随便改，随便加表情。

---

文字负责说清楚。  
表情负责把话说得像人。
