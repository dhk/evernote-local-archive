> **Note:** This document is an early design draft shared for feedback.
> The author is building this primarily for personal use and is validating assumptions publicly before writing much code.

# Local-First Evernote Archive — Design Draft

> **Status:** Early design draft, shared for feedback
> **Intent:** Solve a personal problem first; validate assumptions publicly before building significant tooling

---

## Overview

This document describes a **local-first, open-source workflow** for archiving older Evernote notes while preserving searchability, ownership, and control.

The goal is to help long-time Evernote users reduce note and notebook counts (for example, due to plan limits) **without deleting valuable historical material** or becoming dependent on a proprietary export/import loop.

This is **not** a product, **not** a SaaS, and **not** a replacement for Evernote.
It is a pragmatic, filesystem-based archive pattern that works alongside existing tools.

---

## Motivation

After many years of use, Evernote accounts often accumulate thousands of notes across dozens of notebooks. Recent plan changes and limits force users into difficult trade-offs:

- Delete old notes
- Pay for higher tiers indefinitely
- Export data and lose searchability

This project explores a fourth option:

**Cold-store older notes locally while keeping Evernote as a lightweight index and recall interface.**

The author is building this primarily for personal use and sharing the design openly in case others have similar constraints or can provide early feedback.

---

## Design Principles

### 1. Open Source, Free Forever

- No paid tiers
- No hosted services
- No accounts or authentication
- No telemetry
- No monetization roadmap

If development stops, **everything still works**.

---

### 2. Local-First and Private by Default

- All data lives on the user’s filesystem
- Sync (if used) relies on the user’s own storage (for example, iCloud Drive)
- No data is sent to third parties
- No background services or daemons

---

### 3. Vendor-Resilient

- Uses Evernote’s documented export format (ENEX)
- Uses plain files and directories
- Everything is human-inspectable
- Archive remains usable even if Evernote disappears

---

### 4. Boring, Predictable Technology

- Filesystem as the primary storage layer
- Optional local database for indexing and safety
- No custom sync engines
- No proprietary formats

---

## High-Level Architecture

Evernote (Active Notes + Index)
└── Roll-up Archive Notes (per notebook, per year)

Local Archive (Source of Truth)
├── ENEX files (one per note or per batch)
├── Optional plaintext summaries
└── Optional DuckDB index

**Key idea:**
Evernote remains the *memory interface*.
The filesystem becomes the *archive of record*.

---

## Storage Model

### Cold Storage (Authoritative)

- Notes are exported as ENEX
- Stored locally using a deterministic folder structure

Example layout:

enex/
  notebooks/
    Work/
      2019/
        2019-04-22__project-kickoff__<guid>.enex

ENEX is chosen because it is:
- Lossless
- Documented
- Re-importable into Evernote
- Widely supported

---

### Optional Index / Ledger (DuckDB)

A local DuckDB file may be used to track:
- Which notes have been archived
- Archive paths
- Archive dates
- Summaries and keywords
- Safety checks before deletion

DuckDB is:
- Local-only
- Single-file
- Optional (recommended but not required)

pandas may be used as an interface for inspection and transformation.

---

## Evernote Integration Strategy

### Roll-Up Meta Notes

To stay within Evernote limits, the design avoids creating one Evernote note per archived item.

Instead, it creates:

> **One roll-up note per (notebook, year)**

Example title:
Work — Archived Notes (2019)

Each roll-up contains:
- Note titles
- Last updated dates
- Short summaries
- File links to local ENEX files
- Basic restore instructions

This approach keeps total Evernote note count low while preserving discoverability.

---

## macOS Integration

### Spotlight Search

- Archive folders are stored locally (e.g. in iCloud Drive)
- Spotlight indexes filenames and optional plaintext summaries
- Users can:
  1. Search via Spotlight
  2. Click a result
  3. Open the note in Evernote desktop

No custom indexers are required.

---

### Cross-Device Access

- iCloud Drive (or similar) syncs archive files
- Spotlight indexing happens locally on each Mac
- Evernote desktop is only needed when restoring full notes
- Evernote Web can be used for roll-up notes and summaries

---

## What This Project Is *Not*

This project intentionally does **not** attempt to be:

- A new note-taking application
- A hosted service
- A sync engine
- A mobile app
- A real-time collaboration tool
- A full Evernote replacement

It is a **workflow and set of patterns**, not a platform.

---

## Intended Audience

- Long-time Evernote users hitting plan limits
- Users who value data ownership and longevity
- macOS users who prefer native workflows
- People looking for an “exit hatch” without abandoning their tools

---

## Open Questions (Feedback Welcome)

- Is ENEX the best long-term canonical format?
- Is (notebook, year) the right roll-up granularity?
- Should summaries live in files, a database, or both?
- What failure modes or edge cases are missing?
- What would make this approach brittle in practice?

---

## Scope and Non-Goals (Summary)

### In Scope
- Local-only workflows
- Filesystem-based storage
- Open formats
- Optional local indexing
- Manual or semi-automated processes

### Out of Scope
- Hosted services
- User accounts
- Telemetry or analytics
- Monetization
- Enterprise or multi-user features
- Always-on background services

Any proposal requiring servers or credentials is explicitly out of scope.

---

## Closing Note

This design is shared early and intentionally incomplete.
The goal is to surface flaws and assumptions *before* significant code is written.

Constructive critique is welcome. Email to author@dhk.io
