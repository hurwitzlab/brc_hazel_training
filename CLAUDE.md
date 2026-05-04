# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Training materials for the NCSU Hazel HPC cluster, developed by the Hurwitz Lab at NC State's Bioinformatics Resource Center (BRC). Content covers HPC fundamentals, job submission (LSF scheduler), GNU parallel, and Globus file transfer — all in a bioinformatics context.

## Content Structure

- `notebooks/` — Quarto (`.qmd`) source files; the primary authoring format. Each carries only a `title:` in its front matter; all format settings live in `_quarto.yml`.
- `_quarto.yml` — book project config: parts, chapter order, HTML/PDF format settings.
- `index.qmd` — book preface (landing page).
- `slides/` — PowerPoint decks (`.pptx`) for live workshop sessions, one per day.
- `scripts/` — Example LSF job scripts used in the notebooks. `config.sh` holds all tunable parameters; `run_fastqc.sh` submits a job array; `fastqc.lsf` is the per-sample worker script.
- `images/` — Figures referenced in the README and notebooks.
- `_book/` — rendered output directory (git-ignored).

## Rendering the Book

Render the full handbook to `_book/`:
```bash
quarto render
```

Preview with live reload:
```bash
quarto preview
```

Render a single chapter (standalone, outside the book):
```bash
quarto render notebooks/02_hazel_jobs.qmd
```

Keyboard shortcut in VS Code: `Cmd+Shift+K` renders the active `.qmd` file.

## Book Structure

| Day | Chapter file | Title |
|-----|-------------|-------|
| Day 1 | `notebooks/00_hpc_terminology.qmd` | HPC Terminology |
| Day 1 | `notebooks/01_ncsu_hazel_hpc.qmd` | Getting Started on Hazel |
| Day 1 | `notebooks/02_hazel_jobs.qmd` | Running Jobs on Hazel |
| Day 2 | `notebooks/04_parallel_jobs.qmd` | Parallel Job Arrays |
| Day 3 | `notebooks/03_gnu_parallel.qmd` | GNU Parallel |
| Day 3 | `notebooks/05_job_performance.qmd` | Job Performance |
| Day 4 | `notebooks/globus_basics.qmd` | Globus Basics |

## Scripts Architecture

The LSF scripts follow a three-file pattern:
1. **`config.sh`** — all configurable variables (paths, resources, container). Users edit only this file.
2. **`run_fastqc.sh`** — reads `config.sh`, counts samples, submits a job array via `bsub`.
3. **`fastqc.lsf`** — the actual worker; sources `config.sh`, uses `$LSB_JOBINDEX` to pick its sample from the list, runs FastQC inside an Apptainer container.

Jobs run on Hazel's LSF scheduler (`bsub`). The queue and resource flags (`-n`, `-R`, `-W`) come from `config.sh` exports.
