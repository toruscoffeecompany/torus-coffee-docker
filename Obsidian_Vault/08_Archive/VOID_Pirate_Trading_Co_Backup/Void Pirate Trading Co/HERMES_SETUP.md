# Miss Scarlett Coralsink — Hermes App Template

This is the launch template for Miss Pink's Hermes app on PINKCADY.
Place this folder at:
  D:\Work\VOID Pirate Trading Co\Void Pirate Trading Co - Pink\

## Structure
```
Void Pirate Trading Co - Pink\
├── .hermes\                 <- Hermes app config (this template)
│   ├── skills\              <- her crew-specific skills
│   └── profiles\            <- persona profile wiring
├── work\                    <- her working vault (Hermes project root)
│   ├── 02_Local_Brain\      writable: notes, learning
│   ├── 03_Torus_Coffee\     writable: Torus brand/build work
│   ├── 05_Ships_Log\        writable: daily ship's log
│   └── 06_Artifacts\        local-only: downloads, images
├── prompts.txt              <- her scannable cheat-sheet
├── PERSONALITY.md           <- her voice/persona
└── HERMES_SETUP.md          <- how to launch
```

## Launch (on PINKCADY)
1. Install Hermes (same build as SQUIDSTATION).
2. Point Hermes at this folder as the project root.
3. Hermes reads `PERSONALITY.md` + `prompts.txt` as the active persona.
4. Working directory = `work/` (the lanes above).

## OPSEC
- Never open `_KEY_VAULT` or `.env` files.
- Keys arrive from Captain via secure channel ONLY (see starter pack on
  \\PinkCady\d\00_OhShit_Rebuild_Starter\MISS_PINK_STARTER\04_API_Key_Handoff.md).
- Free-tier only. Every change needs Captain yes/no first.

See the starter pack (00–06) for the full activation sequence.
