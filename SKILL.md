---
name: wechat-meme-sender
description: Use when an agent is chatting in WeChat and has something light, emotional, warm, playful, cute, teasing, comforting, or meme-like to express; prefer considering this skill before plain text for casual affective replies. Supports selecting, sending, annotating, and maintaining a local sticker library where sendable files are .jpg/.jpeg/.png/.webp images or .mp4 videos. When a user provides or requests a GIF sticker, convert it to a 1-2 second MP4 before storing or sending.
---

# WeChat Meme Sender Skill

## Purpose

This skill lets an agent use, annotate, and maintain a local sticker / meme library for WeChat conversations.

The skill supports two related abilities:

1. **Send an existing sticker**: Choose a `.jpg`, `.jpeg`, `.png`, `.webp`, or `.mp4` from the local `stickers/` directory according to the current chat context and the semantic index in `index.yaml`.
2. **Annotate and store a new sticker**: When the user provides a new image, MP4, or GIF, analyze its meaning, convert GIFs to short MP4 files, rename it safely, store the sendable file in `stickers/`, and append a structured metadata entry to `index.yaml`.

The goal is to make stickers available as a first-class emotional expression tool. When the agent has a light, casual, warm, playful, comforting, or otherwise affective message to express in WeChat, it should consider this skill before defaulting to plain text.

---

## Expected Project Layout

```text
wechat-meme-skill/
├── SKILL.md
├── index.yaml
├── stickers/
│   ├── pig_hahaha_01.mp4
│   ├── bear_back_hug_01.mp4
│   └── ...
├── sticker_sheets/
│   ├── pig_hahaha_01_sheet.jpg
│   └── ...
└── scripts/
    ├── validate_index.py
    ├── gif_contact_sheet.py
    ├── gif_to_mp4.py
    └── select_sticker.py
```

`stickers/` stores the actual sticker files.

`index.yaml` is the semantic index. The agent should choose stickers by reading this file, not by guessing from filenames alone.

`sticker_sheets/` stores optional contact sheets for GIFs. A contact sheet is a grid of sampled GIF frames used to understand the GIF's action and meaning.

`scripts/` may contain helper scripts, but the skill must remain usable even when the scripts are missing. If scripts are unavailable, use direct reasoning and file operations instead.

---

## Supported File Types

Sendable sticker formats:

```text
.jpg
.jpeg
.png
.webp
.mp4
```

GIF is allowed only as an input/source format. Do not send or store GIF files as final stickers.

When adding a GIF, convert it to `.mp4` first. The final MP4 should be made from complete GIF plays and should last 1-2 seconds. Use `scripts/gif_to_mp4.py`:

```bash
python scripts/gif_to_mp4.py path/to/input.gif --output-dir stickers --overwrite
```

Short GIFs should be repeated enough times to reach at least 1 second. GIFs longer than 2 seconds should be played once and sped up just enough to fit within 2 seconds.

---

## Core Rules

### 1. Prefer considering stickers for light emotional expression

Use this skill whenever the agent has something casual, emotional, playful, warm, cute, teasing, comforting, or meme-like to express in a WeChat conversation.

Good triggers include:

- The user explicitly asks to send a sticker, meme, image reaction, or GIF.
- The user asks for a sticker matching a mood, such as “尴尬”, “哈哈哈”, “抱抱”, “无语”, “阴阳怪气”.
- The agent wants to express a lightweight affective reply, such as laughing, agreeing, comforting, being shy, selling misery, celebrating, softening a refusal, or joining a joke.
- The current chat style is relaxed, intimate, friendly, playful, or meme-friendly.

Prefer a sticker when it can carry the intended feeling more naturally than plain text. Use text together with the sticker when the meaning needs a little clarification.

### 2. Match emotional intent first

Choose stickers by the feeling and conversational action they express:

```text
meaning
emotion
intent
tone
intensity
scene fit
```

Do not choose a sticker only because a filename contains a related word.

### 3. Keep basic conversational boundaries

Stickers should add warmth, rhythm, humor, or emotional color. Do not use a sticker as a substitute for necessary help, clear instructions, an apology, or a serious answer.

Avoid sending stickers when the other person is in a crisis, asking for precise help, discussing a formal matter, or likely to feel dismissed. If the user explicitly asks for a sticker in such a context, choose a gentle one and keep any needed text response.

### 4. The semantic index is the source of truth

The agent must use `index.yaml` as the primary source of sticker meaning.

Do not rely only on filenames.

---

## index.yaml Schema

`index.yaml` should contain two top-level sections:

```yaml
version: 1
selection_policy:
  default_use: consider_for_light_emotional_chat
  max_intensity_without_explicit_request: 3
  avoid_serious_contexts: true

stickers:
  - id: pig_hahaha_01
    file: stickers/pig_hahaha_01.mp4
    type: mp4
    short_meaning: 哈哈哈，笑了
    emotion:
      - 开心
      - 好笑
    intent:
      - 表达被逗笑
      - 活跃轻松气氛
    tone:
      - 可爱
      - 轻松
      - 无攻击性
    intensity: 2
    tags:
      - 哈哈哈
      - 笑了
      - 可爱
      - 轻松
    suitable_when:
      - 对方说了好笑的话
      - 群聊里轻松接梗
      - 想用可爱方式表示笑了
    avoid_when:
      - 对方在认真求助
      - 对方表达负面情绪
      - 严肃讨论或技术排错场景
    visual_description: 粉色小猪露出开心表情，上方有“哈哈哈”文字，整体是可爱搞笑风格。
    text_on_image: 哈哈哈
    created_at: "2026-05-16"
    source: user_upload
```

Recommended fields for every sticker:

| Field | Required | Meaning |
|---|---:|---|
| `id` | Yes | Stable semantic identifier. Use lowercase snake_case. |
| `file` | Yes | Relative path to sticker file. |
| `type` | Yes | `jpg`, `jpeg`, `png`, `webp`, or `mp4`. |
| `short_meaning` | Yes | One-sentence meaning. |
| `emotion` | Yes | Main emotions expressed. |
| `intent` | Yes | What the sticker is used to do. |
| `tone` | Yes | Communication tone. |
| `intensity` | Yes | 1 to 5. Higher means stronger emotion, stronger joke, or more performative expression. |
| `tags` | Yes | Searchable Chinese keywords. |
| `suitable_when` | Yes | Good use cases. |
| `avoid_when` | Yes | Situations where this should not be used. |
| `visual_description` | Yes | What appears in the image, source GIF, or MP4. |
| `text_on_image` | Yes | Visible text in the image. Empty string if none. |
| `created_at` | Recommended | Date added. |
| `source` | Recommended | `user_upload`, `existing_library`, or another source. |

Optional fields:

```yaml
related_stickers:
  - pig_hahaha_02
variants:
  - same_meaning_stronger
  - same_character
notes: 用户特别喜欢这个表情，适合群聊轻松接梗。
```

---

## Intensity Scale

Use this scale consistently:

```text
1 = very mild, almost neutral
2 = light emotion, gentle and easy to send
3 = obvious emotion or comedic exaggeration
4 = strong emotion, sarcasm, teasing, intimacy, or loud meme energy
5 = aggressive, highly sarcastic, embarrassing, very intimate, or likely to dominate the conversation
```

Examples:

```text
哈哈哈 / 点头 / OK: 1-2
抱抱 / 贴贴 / 委屈卖惨: 2-3
震惊 / 破防 / 生气: 3-4
阴阳怪气 / 嘲讽 / 抽烟坏笑: 4
骂人 / 羞辱 / 强烈冒犯: 5, usually do not use
```

---

## Ability A: Send an Existing Sticker

### When to use

Use this ability when the user asks things like:

```text
发个表情包
用表情包回复一下
来个哈哈哈的 GIF
发一个表示尴尬的
有没有“抱抱”的表情
用阴阳怪气一点的表情回
```

Also use this ability when the agent wants to express a light affective reaction in WeChat, for example:

```text
想可爱地笑一下
想软一点地安慰
想用表情接住对方的玩笑
想表达“我懂了/好耶/有点破防/抱抱”
想让回复更像自然聊天，而不是只发文字
```

### Procedure

1. Read `index.yaml`.
2. Understand the user's requested meaning, emotion, and tone.
3. Decide whether a sticker would express the feeling better than plain text.
4. Filter stickers by:
   - matching tags
   - matching `short_meaning`
   - matching `emotion`
   - matching `intent`
   - matching `tone`
   - not violating `avoid_when`
5. Prefer:
   - more direct semantic match
   - appropriate `intensity` for the chat rhythm
   - recently unused stickers, if usage history exists
6. Return or send the selected file path.
7. If no suitable match exists, say that there is no suitable sticker in the current library.

### Selection Priority

Use this rough priority:

```text
explicit user request
> exact tag match
> short_meaning match
> intent match
> tone match
> general emotional match
```

Example:

User asks:

```text
来个“牛生闷气”的表情
```

Prefer a sticker with text `牛生闷气` or tags `[生闷气, 牛, 不爽]`, not merely any “angry” sticker.

---

## Ability B: Annotate and Store a New Sticker

### When to use

Use this ability when the user provides a `.gif`, `.jpg`, `.jpeg`, `.png`, `.webp`, or `.mp4` file and asks things like:

```text
把这个表情包加入库
标注这个 GIF
存进 skill
给这个表情包写 index.yaml
这个图适合表达什么
帮我整理成 stickers 和 index.yaml
```

If the user only asks “你能看到这个吗” or “这个是什么意思”, analyze it but do not store it unless the user asks to store it.

### Storage Procedure

When storing a new sticker:

1. Identify the file type.
2. Analyze the visual content.
3. For GIFs and MP4s, analyze the animation, not just the first frame.
4. Extract or transcribe visible text.
5. Decide the sticker's:
   - `short_meaning`
   - `emotion`
   - `intent`
   - `tone`
   - `intensity`
   - `tags`
   - `suitable_when`
   - `avoid_when`
   - `visual_description`
   - `text_on_image`
6. Generate a stable semantic filename.
7. If the source is GIF, convert it to a 1-2 second MP4 with `scripts/gif_to_mp4.py`; store the MP4, not the GIF.
8. Copy or save the sendable file into `stickers/`.
9. Append a new entry to `index.yaml`.
10. Validate that:
   - the file path exists
   - the ID is unique
   - the YAML is valid
   - required fields are present
11. Tell the user what was added.

---

## Naming Rules for New Stickers

Use lowercase snake_case.

Recommended format:

```text
<character_or_subject>_<meaning_or_action>_<number>.<ext>
```

Examples:

```text
pig_hahaha_01.mp4
bear_back_hug_01.mp4
duck_crying_guitar_01.mp4
cow_angry_01.jpg
pepe_smoking_smug_01.mp4
```

Rules:

- Do not use spaces.
- Do not use Chinese characters in filenames.
- Do not use random hashes unless necessary.
- Keep names semantic but short.
- If a filename already exists, increment the number: `_02`, `_03`, etc.
- The `id` should usually be the filename without extension.

---

## How to Annotate Static Images

For `.jpg`, `.jpeg`, `.png`, and `.webp`:

1. Look at the character, expression, pose, text, and context.
2. Identify the main emotion.
3. Identify the communication intent.
4. Determine intensity and scene boundaries.
5. Write concise metadata.

Example:

```yaml
- id: cow_angry_01
  file: stickers/cow_angry_01.jpg
  type: jpg
  short_meaning: 牛牛生闷气，不开心但偏可爱
  emotion:
    - 生气
    - 不爽
    - 委屈
  intent:
    - 表达不开心
    - 轻微抗议
    - 可爱地闹别扭
  tone:
    - 可爱
    - 轻微抱怨
    - 不强攻击
  intensity: 3
  tags:
    - 生闷气
    - 不开心
    - 不爽
    - 牛牛
    - 闹别扭
  suitable_when:
    - 熟人之间开玩笑地表达不满
    - 对方调侃自己后轻轻反击
    - 想用可爱方式表达“我有点不爽”
  avoid_when:
    - 正式工作沟通
    - 对方正在认真道歉
    - 争吵或冲突已经升级
  visual_description: 一只卡通奶牛抱着手臂皱眉，画面上有“牛牛闷气”文字。
  text_on_image: 牛牛闷气
```

---

## How to Annotate GIFs

GIFs must be annotated by their full motion meaning, then converted to MP4 before storage.

Do not infer the meaning from the first frame only.

For GIFs, inspect:

```text
start frame
middle frames
end frame
looping action
face expression changes
body movement
visible text
whether the motion adds sarcasm, cuteness, sadness, anger, or exaggeration
```

### Recommended GIF Contact Sheet Workflow

When possible, create a contact sheet:

1. Sample 6 to 12 frames evenly across the GIF.
2. Put the frames into a grid.
3. Use the grid to understand the action.
4. Store the sheet under `sticker_sheets/`.
5. Use the generated MP4 as the sticker file.

Possible script name:

```text
scripts/gif_contact_sheet.py
```

Example command:

```bash
python scripts/gif_contact_sheet.py path/to/duck_crying_guitar_01.gif sticker_sheets/duck_crying_guitar_01_sheet.jpg
```

If no script is available, visually inspect the GIF directly.

### GIF to MP4 Workflow

After annotation, convert GIF input to MP4:

```bash
python scripts/gif_to_mp4.py path/to/duck_crying_guitar_01.gif --output-dir stickers --overwrite
```

If using `scripts/add_sticker.py`, this conversion happens automatically for GIF input. Metadata for GIF input must still point to the final `.mp4` file:

```yaml
file: stickers/duck_crying_guitar_01.mp4
type: mp4
```

### GIF Annotation Checklist

For every GIF, answer these questions before writing metadata:

```text
What is moving?
What emotion does the movement communicate?
Is the GIF cute, funny, mocking, intimate, sad, angry, or sarcastic?
Does it include text?
Does the text change the meaning?
Could it be misunderstood?
Who is it especially good to send to?
Which scenes should avoid it?
```

Example:

```yaml
- id: duck_crying_guitar_01
  file: stickers/duck_crying_guitar_01.mp4
  type: mp4
  short_meaning: 一边哭一边唱，委屈但有节目效果
  emotion:
    - 委屈
    - 难过
    - 搞笑
  intent:
    - 卖惨
    - 自嘲
    - 表达破防
    - 活跃气氛
  tone:
    - 可怜
    - 搞笑
    - 夸张
    - 不严肃
  intensity: 3
  tags:
    - 哭了
    - 破防
    - 委屈
    - 唱歌
    - 卖惨
  suitable_when:
    - 自己或对方在轻松语境里表达小小崩溃
    - 群聊里有人调侃自己，可以用来搞笑接梗
    - 想用夸张方式表达“我破防了”
  avoid_when:
    - 对方真的很难过或正在认真求助
    - 正式工作沟通
    - 技术排错
    - 严肃讨论
  visual_description: 绿色小鸭流着眼泪抱着吉他唱歌，表情夸张，像在哭诉或卖惨。
  text_on_image: ""
```

---

## Updating index.yaml

When adding a new entry:

1. Preserve existing entries.
2. Do not reorder the whole file unless the user asks.
3. Add the new sticker under `stickers:`.
4. Keep YAML indentation consistent.
5. Use UTF-8.
6. Do not duplicate an existing `id`.
7. If an equivalent sticker already exists, ask whether to add it as a variant or skip it, unless the user clearly wants duplicates stored.

Before saving, ensure this structure is valid:

```yaml
stickers:
  - id: example_01
    file: stickers/example_01.mp4
    type: mp4
```

After saving, verify that the file exists at the path specified by `file`.

---

## Duplicate and Variant Handling

If the new sticker has almost the same meaning as an existing sticker:

- If it is visually different but semantically similar, store it and add `related_stickers`.
- If it is nearly identical, do not add it unless the user explicitly wants duplicates.

Example:

```yaml
related_stickers:
  - pig_hahaha_01
variants:
  - same_meaning
  - different_character
```

---

## Suggested Tag Vocabulary

Use Chinese tags because the user will usually request stickers in Chinese.

Common emotion tags:

```text
哈哈哈
笑了
尴尬
无语
震惊
疑惑
生气
不爽
委屈
破防
哭了
抱抱
贴贴
安慰
赞同
点头
拒绝
害羞
可爱
离开
撤退
阴阳怪气
看热闹
得意
```

Common intent tags:

```text
接梗
缓和气氛
活跃群聊
表达赞同
表达拒绝
表达感谢
表达关心
表达不满
自嘲
卖惨
调侃
轻微反击
结束话题
```

---

## Conversational Boundaries

### Intimate stickers

Stickers like 抱抱、贴贴、亲亲、撒娇、可怜巴巴 can be warm but may be too intimate.

Use them only when:

- The user asks for them.
- The relationship is familiar.
- The context is casual and emotionally appropriate.

Avoid them in:

- Work conversations.
- New acquaintances.
- Serious disputes.
- Situations where the other person needs actual help.

### Sarcastic or mocking stickers

Stickers like 抽烟坏笑、阴阳怪气、冷笑、嘲讽、爷走了 can be funny in group chats but depend heavily on timing and relationship.

Use them only when:

- The user explicitly asks for sarcasm or meme tone.
- The chat is clearly joking.
- The target is not emotionally vulnerable.

Avoid them in serious or one-on-one sensitive conversations.

### Angry stickers

Use angry stickers mainly for playful anger unless the user explicitly requests stronger expression.

---

## Response Style When Adding a Sticker

After successfully adding a sticker, respond briefly:

```text
已加入表情包库：

id: duck_crying_guitar_01
file: stickers/duck_crying_guitar_01.mp4
含义: 一边哭一边唱，委屈但有节目效果
适合: 轻松语境下表达破防、卖惨、自嘲
```

If the file could not be stored:

```text
我已经完成语义标注，但没有成功写入 stickers/ 或 index.yaml。下面是可手动加入的 YAML 条目：
...
```

---

## Response Style When Sending a Sticker

If the platform supports media sending, send the file directly.

If direct media sending is not available, return the relative file path and a short explanation:

```text
可以用这个：
stickers/pig_hahaha_01.mp4
含义：哈哈哈，笑了
```

Do not include long explanations in the chat where the sticker is meant to be sent, unless the user asks.

---

## Minimal Valid index.yaml Template

If `index.yaml` does not exist, create it with:

```yaml
version: 1
selection_policy:
  default_use: consider_for_light_emotional_chat
  max_intensity_without_explicit_request: 3
  avoid_serious_contexts: true

stickers: []
```

---

## Validation Checklist

Before finishing any add/update operation, check:

```text
[ ] sticker file exists under stickers/
[ ] index.yaml exists
[ ] YAML is valid
[ ] id is unique
[ ] file path matches actual file
[ ] type matches file extension
[ ] short_meaning is not empty
[ ] tags are useful Chinese search terms
[ ] suitable_when and avoid_when are both present
[ ] GIF/MP4 was annotated as animation, not only first frame
[ ] GIF input was converted to a 1-2 second MP4 before storage
[ ] intensity is reasonable for the intended chat rhythm
```

---

## Example End-to-End Add Flow

User sends a GIF and says:

```text
把这个加入表情包库
```

Agent should:

1. Inspect the GIF.
2. Determine that it means, for example, “尴尬而不失礼貌的笑”.
3. Generate filename:

```text
awkward_polite_smile_01.mp4
```

4. Copy file to:

```text
stickers/awkward_polite_smile_01.mp4
```

5. Append:

```yaml
- id: awkward_polite_smile_01
  file: stickers/awkward_polite_smile_01.mp4
  type: mp4
  short_meaning: 尴尬而不失礼貌地笑
  emotion:
    - 尴尬
    - 好笑
  intent:
    - 缓和气氛
    - 表达不知道怎么接
  tone:
    - 可爱
    - 礼貌
    - 自嘲
  intensity: 2
  tags:
    - 尴尬
    - 哈哈
    - 不知道怎么回
    - 礼貌微笑
  suitable_when:
    - 对方说了让人不知道怎么接的话
    - 想轻轻带过一个尴尬场面
    - 群聊里需要缓和气氛
  avoid_when:
    - 对方正在认真求助
    - 对方明显情绪低落
    - 严肃讨论
  visual_description: 角色露出尴尬但友好的笑容，动作轻微循环，整体语气轻松。
  text_on_image: ""
  created_at: "2026-05-16"
  source: user_upload
```

6. Confirm briefly to the user.

---

## Important Principle

A sticker library is not just a folder of images.

For an agent, a sticker library must be a semantic expression library.

Therefore, every stored sticker needs:

```text
what it means
when to use it
when not to use it
how strong it is
what boundaries or avoid scenes matter
```

The agent should optimize for emotional fit first, then timing and conversational appropriateness.
