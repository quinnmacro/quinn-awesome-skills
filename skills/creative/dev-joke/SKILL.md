---
name: dev-joke
description: |
  Generate developer jokes, coding humor, and tech memes.
  Use when user asks for "joke", "funny", "make me laugh", "程序员笑话", 
  or needs a morale boost during debugging sessions.
version: 1.0.0
author: quinnmacro
---

# Developer Joke Generator

Generate programming humor to lighten the mood during long coding sessions.

## Trigger Phrases

- "讲个笑话"
- "程序员笑话"
- "来个段子"
- "哄我开心"
- "debug 太累了"
- "tell me a joke"
- "make me laugh"

## Joke Categories

### Classic 经典笑话

```markdown
Q: Why do programmers prefer dark mode?
A: Because light attracts bugs.

Q: Why do Java developers wear glasses?
A: Because they can't C#.

Q: A SQL query walks into a bar, walks up to two tables and asks...
A: "Can I join you?"
```

### Debug Life 调试人生

```markdown
Debug 的人生三阶段：
1. "这代码怎么可能出错？"
2. "这代码怎么能跑？"
3. "别碰它，能跑就行。"

The three stages of debugging:
1. "That can't be happening."
2. "That doesn't happen on my machine."
3. "That shouldn't happen."
```

### Tech Stack Humor 技术栈幽默

```markdown
前端说："界面很美，只是功能还没做。"
后端说："功能都有，只是接口还没定。"
测试说："都没问题，只是用户不会用。"
产品说："都做完了，只是需求又变了。"

Why React developers are always calm?
Because they have no state. (this.setState...)
```

### Git Humor Git 幽默

```markdown
git commit -m "fixed bug"
git commit -m "really fixed bug"
git commit -m "actually fixed bug this time"
git commit -m "please work"
git commit -m "I give up"
git push --force

A man is smoking a cigarette and blowing smoke rings.
He says to his friend: "I'm a Git user."
Friend: "How do you know?"
He blows three more smoke rings and says: "Merge conflict resolved."
```

### Coffee & Deadlines 咖啡与截止日期

```markdown
程序员血型：
A型 - 咖啡
B型 - 更多的咖啡
AB型 - 咖啡 + 红牛
O型 - 已经不需要睡眠了

Definition of "it works on my machine":
The universal excuse that has ended more careers than incompetence.
```

## Usage

```bash
# Random joke
bash scripts/llm.sh "Tell me a programming joke" --system "You are a witty programmer comedian"

# Joke about specific technology
bash scripts/llm.sh "Tell me a JavaScript joke" --json

# Joke in Chinese
bash scripts/llm.sh "讲一个程序员笑话" --system "你是一个幽默的程序员"
```

## Interactive Mode

When user seems frustrated (e.g., during debugging), offer:

```
1. 🎯 A relatable joke about their current struggle
2. 💪 An encouraging "you got this" message
3. 🍵 A reminder to take a break

Example response when user says "I've been debugging for 3 hours":
---
Look, even the best of us have been there. Here's one for you:

"I have 99 problems, and debugging is 97 of them.
The other 2 are merge conflicts."

You've got this! Take a deep breath. Maybe grab some coffee?
The bug is probably a missing semicolon anyway. 😄
---
```

## Output Format

```markdown
## 😄 [Category Emoji] [Joke Title]

[Joke content]

---
*Why it's funny*: [Brief explanation for non-native speakers]
```

## Special Situations

### When User is Frustrated
```
Acknowledge their frustration first
Then deliver an empathetic joke
End with encouragement
```

### When User Asks for Specific Topic
```
Tailor joke to their technology:
- "JavaScript joke" → async/callback/promise humor
- "Python joke" → indentation/import humor
- "Git joke" → commit/push/merge humor
- "Database joke" → SQL/NoSQL humor
```

### When User Wants "One More"
```
Generate a series of related jokes
Build comedic momentum
End on a strong punchline
```
