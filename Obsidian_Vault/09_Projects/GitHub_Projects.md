# GitHub Projects – Task Tracking
_Last updated: 2026-07-22_

## Mirror of Trello Columns
Use this when moving board logic into GitHub Issues/Projects.

| Column   | Meaning                                                         | GitHub equivalent                |
|----------|-----------------------------------------------------------------|----------------------------------|
| Backlog  | Not ready for work; needs definition or dependencies            | Issue, no label, open            |
| Ready    | Fully described, no blockers, assignee ready to start           | Issue + `ready` label            |
| In Progress | Actively being worked on                                      | Issue + `in-progress` label      |
| Review   | Needs approval or merge; awaiting QA/sign-off                   | PR in `develop`/`main`, or issue with `review` label |
| Done     | Merged/released/closed with outcome captured                    | Closed issue/PR, item in project |

## Mapping Guidance
- One GitHub issue per card.
- Link PRs to the issue via keywords: `Fixes #123`, `Closes #123`.
- Use GitHub Projects view to mimic the board; keep Status field aligned to the columns above.
- Keep non-code work in issues too: docs, ops, finance review.

## Maintainers / Assignees
- Owner: issue/pull-request reviewer and final approver.
- Ops Contributor: inventory, finance automation, ops rules.
- Web Contributor: Next.js build, deploy, Supabase decisions.

## Expected Fields
- Title: short verb + noun.
- Description: goal, acceptance criteria, linked docs.
- Labels: `area:website`, `area:ops`, `area:finance`, `area:legal`, `area:growth`.
- Milestone: quarter or release if applicable.
