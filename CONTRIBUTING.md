# Contributing to quinn-awesome-skills

Thank you for your interest in contributing! This document provides guidelines for adding new skills or improving existing ones.

## Adding a New Skill

### 1. Create Skill Directory

```bash
mkdir -p skills/your-skill-name/scripts
```

### 2. Create SKILL.md

Every skill must have a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: your-skill-name
description: |
  Clear, concise description of what the skill does.
  Include trigger phrases that should activate this skill.
version: 1.0.0
author: your-username
---

# Skill Title

Detailed instructions for Claude...
```

### 3. Add Supporting Scripts (Optional)

If your skill needs scripts, place them in `scripts/`:

```bash
skills/your-skill-name/
├── SKILL.md
├── scripts/
│   ├── main.sh
│   └── helper.py
└── references/
    └── docs.md
```

### 4. Update README

Add your skill to the main README.md skills table:

```markdown
| [your-skill-name](skills/your-skill-name/) | Brief description | 🏷️ Category |
```

## Skill Guidelines

### YAML Frontmatter Required Fields

| Field | Description |
|-------|-------------|
| `name` | Unique skill identifier (lowercase, hyphen-separated) |
| `description` | 2-3 sentences describing functionality and triggers |
| `version` | Semantic version (e.g., `1.0.0`) |
| `author` | GitHub username |

### SKILL.md Best Practices

1. **Clear triggers**: Include phrases that should activate the skill
2. **Step-by-step workflow**: Claude follows structured instructions better
3. **Code examples**: Show exactly how to run scripts
4. **Error handling**: Document what to do when things fail

### Script Best Practices

1. **Use `set -euo pipefail`** for bash scripts
2. **Check dependencies** and provide installation instructions
3. **Return clean output** - JSON for structured data, plain text otherwise
4. **Handle errors gracefully** - meaningful error messages

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b add-skill-name`
3. Add your skill following the structure above
4. Update README.md
5. Test your skill locally
6. Submit PR with description of changes

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open an issue for discussion before major changes.
