# Obsidian Plugin Deep-Dive Audit — 2026-08-06
Generated: 2026-08-06T07:15:00.000000+00:00
Status: COMPLETED

## Plugin inventory (21 installed)
| Plugin | Version | Config Status | Priority | Improvement Plan |
|--------|---------|---------------|----------|------------------|
| calendar | 1.5.10 | default | P3 | Enable daily note integration with periodic-notes |
| dataview | 0.5.68 | default | P2 | Create Dataview queries for open issues/automation dashboard |
| periodic-notes | 0.0.17 | configured | P1 | Daily/weekly/monthly templates set; enable daily toggle |
| templater-obsidian | 2.24.3 | configured | P2 | templates_folder set; add task template functions |
| quickadd | 2.21.0 | 3 macros imported | P2 | Add crew comms/ooda status macros |
| obsidian-git | 2.38.6 | autoCommit=30m, autoPush=60m | P1 | Verify git credentials; enable autoPull on startup |
| obsidian-excalidraw-plugin | 2.26.4 | default | P3 | Enable canvas export to PNG for crew briefings |
| obsidian-icon-folder | 2.14.7 | default | P3 | Standardize folder icons for ops/vault folders |
| obsidian-importer | 1.9.1 | default | P3 | Use for Evernote/Notion vault migration if needed |
| obsidian-kanban | 2.0.51 | default | P3 | Create OODA P1/P2/P3/Done board |
| obsidian-linter | 1.32.0 | lintOnSave=False | P2 | Enable lintOnSave; create crew style guide |
| obsidian-livesync | 1.0.5 | useWebRTC=None | P2 | Configure peer name + relay for PINKCADY crew |
| obsidian-markmind | 3.5.7 | default | P3 | Enable mindmap export for sprint planning |
| obsidian-minimal-settings | 9.0.0 | default | P2 | Standardize vault theme/typography |
| obsidian-outliner | 4.10.2 | default | P2 | Enable keyboard shortcuts for bullet manipulation |
| obsidian-style-settings | 1.0.9 | default | P2 | Sync style with minimal-settings |
| obsidian-tasks-plugin | 8.3.0 | taskFolder=None | P2 | Set taskFolder=00_Inbox/01_Daily; link to periodic-notes |
| omnisearch | 1.30.1 | engine=None | P2 | Enable fuzzy search; configure vault-wide indexing |
| smart-connections | 4.7.1 | default | P3 | Enable AI graph for vault connections |
| table-editor-obsidian | 0.23.2 | default | P2 | Create standard tables for inventory/orders |
| tag-wrangler | 0.6.4 | default | P3 | Organize vault tags; remove duplicates |

## Quick wins
1. Enable lintOnSave in obsidian-linter
2. Set taskFolder in obsidian-tasks-plugin
3. Enable daily toggle in periodic-notes
4. Configure obsidian-livesync peer name
5. Import 5 QuickAdd macros for crew comms/ooda/trello

## Medium-term
1. Create Dataview automation dashboard
2. Standardize minimal-settings/style-settings
3. Create obsidian-kanban board for OODA tasks
4. Enable omnisearch engine

## Long-term
1. Smart connections graph for vault AI
2. Excalidraw canvas export workflow
3. Markmind sprint planning exports
4. Tag wrangling standardization
