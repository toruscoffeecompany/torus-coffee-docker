# How to Use Trello Boards

This guide explains how to use the Obsidian-native Trello board structures in `09_Projects/Trello_Boards/` for Torus Coffee Company LLC operations.

## Overview

Each board mirrors a Trello board using Markdown files. Lists are folders; cards are individual `.md` files with YAML frontmatter. Cross-links let you navigate between cards, lists, and boards directly from Obsidian.

## Boards at a Glance

| Board | Purpose | Path |
|-------|---------|------|
| Torus Ops | Daily operations, inventory, production, fulfillment | `Torus_Ops/` |
| Website Rebuild | Website redesign, content, SEO, launch | `Website_Rebuild/` |
| Business Docs | Compliance, policies, procedures | `Business_Docs/` |

Each board has **5 lists** (Kanban columns):
1. **Backlog** — Tasks waiting to be prioritized
2. **To Do** — Prioritized tasks ready to start
3. **In Progress** — Tasks actively being worked on
4. **Review** — Tasks awaiting verification or approval
5. **Done** — Completed and shipped tasks

## Card Anatomy

Every card `.md` file follows this structure:

```yaml
---
type: card
board: Torus_Ops
status: Backlog
priority: medium
tags: []
created: 2026-08-02
assignee: 
due: 
---

# {{title}}

## Description

## Checklist

- [ ] 

## Notes
```

### Frontmatter Fields

| Field | Description | Values |
|-------|-------------|--------|
| `type` | Always `card` | `card` |
| `board` | Board folder name | `Torus_Ops`, `Website_Rebuild`, `Business_Docs` |
| `status` | Current list the card lives in | `Backlog`, `To_Do`, `In_Progress`, `Review`, `Done` |
| `priority` | Urgency level | `low`, `medium`, `high` |
| `tags` | Categorization for filtering | Array of strings, e.g. `[inventory, production]` |
| `created` | ISO date | `YYYY-MM-DD` |
| `assignee` | Team member responsible | Name or `@mention` |
| `due` | Deadline | `YYYY-MM-DD` or blank |

## Creating a New Card

1. **Pick a template** from the board's `Templates/` folder. Use the specialized template that best fits the task:
   - **Torus Ops**: Generic, Inventory, Production, Fulfillment
   - **Website Rebuild**: Generic, Content, SEO, Dev
   - **Business Docs**: Generic, Compliance, Policy, Procedure
2. **Copy** the template into the appropriate list folder (e.g., `Torus_Ops/To_Do/`).
3. **Rename** the file using a concise title (e.g., `Card_Weekly_Inventory_Count.md`).
4. **Fill in the frontmatter**: set `status`, `priority`, `tags`, `assignee`, `due`.
5. **Complete the body**: write the description, checklists, and notes specific to the task.
6. **Link the card**: add a link to the card from the list file's `## Cards` section.

   ```markdown
   - [[Card_Weekly_Inventory_Count|Weekly Inventory Count]]
   ```

## Moving a Card Between Lists

When a card advances through the workflow:

1. Move the `.md` file from one list folder to the next (e.g., `To_Do/` → `In_Progress/`).
2. Update the `status` field in the card's YAML frontmatter.
3. Update the link in both the source and destination list files.

## Sample Cards

Each list contains 2–3 sample cards showing realistic tasks for Torus Coffee Company. These are ready to copy, rename, and fill in. Browse them to understand how each template type is used.

## Tips

- **Keep titles scannable**: `Card_Run_Batch_Cold_Brew` not `Card_Do_the_thing`
- **Use tags consistently**: see existing cards for tag conventions
- **Update status immediately**: move cards as soon as work begins or completes
- **Review Done weekly**: use the Done list for retrospectives
- **Keep templates updated**: if you find yourself rewriting the same checklist, add a new template

## Obsidian Navigation

- Use `[[` to link to any card, list, or board
- Use graph view to see task relationships
- Use tag filter (`#inventory`) to view all tasks of a type across boards
