# Projects Repository

This repository contains experimental projects and solution workspaces.

## New: project idea exporter

Use `/tmp/workspace/AllanOnyonka-ltsm/Projects/scripts/export_project_ideas.py` to import project ideas from Obsidian or any markdown-based agent workflow.

The script reads markdown files and creates one folder per idea with:

- `idea.md` (original markdown)
- `README.md` (normalized project brief)
- language-specific starter code (`main.py`, `index.js`, `index.ts`, `main.go`, `main.rs`, or `starter.txt`)

## Usage

```bash
python /tmp/workspace/AllanOnyonka-ltsm/Projects/scripts/export_project_ideas.py \
  --source /path/to/obsidian-export-or-md-folder \
  --output /tmp/workspace/AllanOnyonka-ltsm/Projects/project_ideas
```

Add `--overwrite` to reuse existing generated folders.

## Expected markdown format

The importer supports plain markdown and optional frontmatter:

```md
---
title: Voice Symptom Tracker
language: python
description: Build an MVP that records voice and predicts risk level
---

# Voice Symptom Tracker

Idea details from Obsidian or an agent-generated brief.
```
