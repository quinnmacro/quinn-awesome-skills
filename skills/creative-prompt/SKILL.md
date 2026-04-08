---
name: creative-prompt
description: |
  Generate creative prompts for writing, design, brainstorming, and ideation.
  Use when user asks for "creative ideas", "writing prompts", "design inspiration", 
  "brainstorm help", or "give me ideas for".
version: 1.0.0
author: quinnmacro
---

# Creative Prompt Generator

Generate creative prompts for various creative tasks: writing, design, art, brainstorming.

## Trigger Phrases

- "给我一些创意"
- "帮我头脑风暴"
- "写个故事灵感"
- "设计灵感"
- "创意提示"
- "给我点子"

## Categories

### Writing Prompts 写作提示

Generate story starters, character ideas, plot twists:

```
Ask user for:
- Genre (sci-fi, fantasy, romance, thriller, etc.)
- Mood (dark, light, mysterious, humorous)
- Length (short story, novel, flash fiction)

Then generate 3-5 unique prompts with:
- Opening hook
- Character concept
- Central conflict
- Unexpected twist element
```

### Design Prompts 设计提示

Generate design challenges and inspiration:

```
Ask user for:
- Medium (logo, poster, UI, illustration)
- Style (minimal, maximal, retro, futuristic)
- Purpose (commercial, personal, experimental)

Then generate:
- Design brief
- Color palette suggestions
- Typography direction
- Reference mood board keywords
```

### Brainstorm Prompts 头脑风暴

Generate ideation starting points:

```
Ask user for:
- Domain (product, feature, business, problem)
- Constraints (time, budget, technology)
- Target audience

Then use SCAMPER technique:
- Substitute 替代
- Combine 组合
- Adapt 调整
- Modify 修改
- Put to other uses 其他用途
- Eliminate 消除
- Reverse 反转
```

## Usage

```bash
# Generate creative writing prompt
bash scripts/llm.sh "Generate a creative writing prompt for sci-fi genre" --system "You are a creative writing teacher"

# Generate design inspiration
bash scripts/llm.sh "Give me 5 logo design ideas for a tech startup" --json

# Brainstorm product features
bash scripts/llm.sh "Brainstorm 10 unique features for a note-taking app"
```

## Output Format

Always structure output as:

```markdown
# Creative Prompt: [Title]

## Concept
[One sentence core idea]

## Details
- **Hook**: [Attention-grabbing element]
- **Twist**: [Unexpected element]
- **Emotion**: [Target emotional response]

## Starting Point
[Concrete beginning - first line, visual, or question]

## Variations
1. [Alternative direction 1]
2. [Alternative direction 2]
3. [Alternative direction 3]
```

## Examples

### Writing Prompt
```
# The Last Algorithm

## Concept
In a world where AI has solved every problem, one programmer discovers 
the last unsolved algorithm - and it's a love letter.

## Details
- **Hook**: "The code was beautiful, but it wasn't mine."
- **Twist**: The algorithm predicts human emotions, not outcomes
- **Emotion**: Melancholy wonder

## Starting Point
"Every algorithm has an answer. Except this one."
```

### Design Prompt
```
# Neon Wilderness

## Concept
A branding identity that merges organic nature with cyberpunk aesthetics.

## Details
- **Hook**: Sharp geometric leaves glowing in electric green
- **Twist**: Traditional botanical illustration meets glitch art
- **Emotion**: Futuristic nostalgia

## Color Palette
- Electric Green #39FF14
- Deep Purple #2D1B4E
- Soft White #F0F0F0
- Neon Pink #FF10F0

## Typography
- Display: Orbitron or Share Tech Mono
- Body: Space Grotesk
```
