# Evernote Local Archive (Design Draft)

This repository contains early design notes for a **local-first, open-source workflow** to archive old Evernote notes while preserving searchability and user control.

This is **not a product**, **not a SaaS**, and **not a replacement for Evernote**.

I’m solving this problem for myself first and sharing the design publicly in case others find it useful or can help point out flaws before much code is written.

## What this is
- A filesystem-first archive using standard export formats (e.g. ENEX)
- Designed to keep all data local and private
- Intended to work with existing tools (Evernote, Spotlight, iCloud Drive)
- Free and open source by intent

## What this is not
- A hosted service
- A sync engine
- A note-taking app
- A promise of long-term maintenance

## Tools
### Split an ENEX into per-note files
This repo includes a small helper to split a notebook ENEX export into one ENEX file per note.

Example:
```bash
python split_evernote_export.py "/Users/dhk/Downloads/evernote-export/!!Knee Replacement Surgery.enex"
```

By default, output goes to a sibling folder named `!!Knee Replacement Surgery-notes/`.
You can override with:
```bash
python split_evernote_export.py "/path/to/notebook.enex" --output-dir "/path/to/output"
```

## Issues and Questions
Have a question, suggestion, or bug report? Please open a GitHub issue for this repo.

## Status
Design-only. Feedback welcome.

See [DESIGN.md](DESIGN.md) for details.
