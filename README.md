# Evernote Local Vault (Design Draft)

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
This repo includes a helper to split a notebook ENEX export into one ENEX file per note, and optionally generate a compendium index note.

Example using the demo notebook in this repo:
```bash
python split_evernote_export.py "/Users/dhk/Documents/dev/evernote-local-archive/samples/food-demo-notes.enex"
```

By default, output goes to a sibling folder named `food-demo-notes-notes/`.
You can override with:
```bash
python split_evernote_export.py "/path/to/notebook.enex" --output-dir "/path/to/output"
```

Additional features:
- `--with-index`: write a compendium ENEX with a table of notes, human-readable dates, and “Show in Finder” links.
- `--index-title`: set the compendium note title (default: `vault-index`).
- `--index-name`: set the compendium filename (default: `vault-index.enex`).
- `--add-comment`: add a short comment near the top of the compendium index.
- `--dry-run`: parse and plan outputs without writing files.
In the case where you want to include comments in the constructed compendium note, use the `--add-comment` option.

## Output format
This tool writes standard Evernote `.enex` files:
- Each output file is a valid ENEX export containing a single `<note>`.
- The optional compendium file is also a single-note ENEX export with a summary table.

## Import back into Evernote
In Evernote desktop:
1. Open **File → Import**.
2. Select the `.enex` file you want to restore.
3. Confirm the import location and finish.

Tip: You can import a single note ENEX or the compendium file.

## Issues and Questions
Have a question, suggestion, or bug report? Please open a GitHub issue for this repo.

## Status
Design-only. Feedback welcome.

See [DESIGN.md](DESIGN.md) for details.
