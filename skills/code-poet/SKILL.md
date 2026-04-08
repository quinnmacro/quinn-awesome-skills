---
name: code-poet
description: |
  Transform code into poetry, write code-inspired poems, or explain code poetically.
  Use when user asks for "code poetry", "poetic explanation", "代码诗", 
  "explain code beautifully", or wants creative code documentation.
version: 1.0.0
author: quinnmacro
---

# Code Poet - 代码诗人

Transform the beauty of code into the beauty of words.

## Trigger Phrases

- "把代码变成诗"
- "用诗意解释这段代码"
- "代码诗"
- "code poetry"
- "write a poem about this code"
- "explain like I'm reading poetry"

## Poetry Styles

### Haiku 俳句 (5-7-5)

```
Function calls function
Recursion endless and deep
Stack overflow now
```

```
变量未定义
空指针异常闪现
调试到天明
```

### Free Verse 自由诗

```markdown
# The Promise

I await your resolution,
Suspended in the event loop's embrace.
Will you resolve with sweet data,
Or reject with cold error?

The .then() chains stretch infinitely,
Each callback a heartbeat,
Waiting for your async soul
To finally return.
```

### Sonnet 十四行诗

```markdown
# A Love Letter to My Codebase

Shall I compare thee to a clean refactor?
Thou art more lovely and more maintainable.
Rough bugs do shake the darling branches' factor,
And summer's deadline hath all too short a stable.

Sometime too hot the CPU's eye shines,
And often is your memory constrained;
And every algorithm sometime declines,
By chance, or nature's changing course, unchained.

But thy eternal logic shall not fade,
Nor lose possession of that fair O(n);
Nor shall Death brag thou wander'st in his shade,
When in eternal lines to time thou run'st on.

  So long as men can breathe, or eyes can see,
  So long lives this, and this gives life to thee.
```

### Chinese Classical 古诗词

```markdown
# 调试有感

千行代码锁眉头，
一虫藏身何处求？
断点设尽无觅处，
原来分号漏西楼。

# 算法吟

递归深处递归深，
栈帧层层到古今。
基例若失归何处，
内存泄漏泪沾襟。
```

## Usage

### Transform Code to Poetry

```bash
# Haiku from function
bash scripts/llm.sh "Write a haiku about this code:
function fibonacci(n) {
  return n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2);
}"

# Free verse from algorithm
bash scripts/llm.sh "Write a free verse poem explaining binary search algorithm"

# Chinese poem from code
bash scripts/llm.sh "用七言绝句写一段关于死循环的诗"
```

### Explain Code Poetically

When user shares code, explain it with poetic language:

```markdown
## 📜 The Tale of async/await

Once upon a callback hell so deep,
Where pyramid code made developers weep,
Came async/await, a promise so sweet,
Making asynchronous code finally neat.

```javascript
async function fetchUserTale() {
  try {
    const hero = await fetchHero();    // The protagonist arrives
    const quest = await fetchQuest();  // Their journey begins
    const fate = await resolveQuest(); // Destiny unfolds
    return { hero, quest, fate };      // Story complete
  } catch (tragedy) {
    console.error('Alas!', tragedy);   // Even heroes fall
  }
}
```

Here, `await` is patience personified,
Pausing execution with graceful pride.
The code flows like a story well-told,
Not tangled in callbacks of old.
```

## Output Formats

### Code Haiku
```markdown
## 🎴 Haiku: [Title]

[5 syllables]
[7 syllables]
[5 syllables]

*Context*: [What code this describes]
```

### Code Sonnet
```markdown
## 📜 Sonnet: [Title]

[14 lines of iambic pentameter]
[Quatrain 1: Setup]
[Quatrain 2: Development]
[Quatrain 3: Twist]
[Couplet: Resolution]

*Technical note*: [Brief explanation]
```

### Code 唐诗
```markdown
## 🏯 [标题]

[第一句]，
[第二句]。
[第三句]，
[第四句]。

*注释*：[代码含义]
```

## Examples by Language

### Python
```
Indent, indent,
My whitespace must align.
Python smiles upon my code,
Tabs or spaces—never both.
```

### JavaScript
```
Undefined is not a function,
Says the error in console red.
Type coercion, my old friend,
'1' + 1 equals '11' instead.
```

### Git
```
Thou shalt not push to main,
The sacred rule of all teams.
Yet here I stand, head in hands,
After git push --force screams.
```

### Regex
```
/^([A-Z][a-z]+)\s+(\d+)$/
    
Some people, when confronted with a problem,
think "I know, I'll use regular expressions."
Now they have two problems.
But oh, the beauty when they match.
```

## Integration with Development

### Commit Message Poetry
```
feat: A sonnet for login

When user clicks the button bold,
And credentials fill the form of old,
Our function validates with grace,
And grants them entry to this space.

Fixes #42
```

### PR Description Poetry
```
## 📝 The Ballad of Button Refactor

Once there were buttons, scattered wide,
No pattern shared, no style to guide.
Now they march in unified array,
Component-built, in neat display.

### Changes
- Unified button styles
- Extracted Button component
- Added variant props
```

### Code Comment Poetry
```javascript
// In the realm of async, patience is key
// Await the promise, let it be
// For rush not the resolution's sweet embrace
// Lest you face the void of undefined space
async function gentleFetch(url) {
  return await fetch(url);
}
```
