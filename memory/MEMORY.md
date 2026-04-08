# Memory Index

This directory contains project memories that persist across sessions.

## Purpose

Memories store information about:
- User preferences and patterns
- Project decisions and context
- Lessons learned from past work
- External references

## Memory Types

| Type | Purpose |
|------|---------|
| `user` | User role, preferences, expertise |
| `feedback` | Guidance on how to approach work |
| `project` | Ongoing work, goals, initiatives |
| `reference` | Pointers to external resources |

## Index

- [Project Context](project_context.md) - Overall project context and goals

## Notes

- Memory files use YAML frontmatter with `name`, `description`, `type` fields
- Keep memories concise and focused
- Update or remove stale memories
- Memory is git-tracked for portability
