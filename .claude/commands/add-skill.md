---
allowed-tools: Bash(mkdir:*), Bash(touch:*), Bash(ls:*), Edit, Write
description: Create a new skill with proper structure
---

## Context

- Skills directory: !`ls -la skills/`

## Your Task

Create a new skill with the following structure:

1. Ask the user for:
   - Skill name (lowercase, hyphen-separated)
   - Brief description
   - Category (content, automation, development, etc.)

2. Create the directory structure:
   ```
   skills/{skill-name}/
   ├── SKILL.md
   ├── scripts/
   └── references/
   ```

3. Generate SKILL.md with template:
   ```markdown
   ---
   name: {skill-name}
   description: |
     {description}
   version: 1.0.0
   author: quinnmacro
   ---

   # {Skill Title}

   ## Usage

   ## Examples

   ## Notes
   ```

4. Update README.md skills table
5. Update CHANGELOG.md

Create all files in a single response.
