# Subtitle Sanitation Toolkit — Roadmap

## Core Positioning
This project targets **subtitle sanitation**: repairing, restructuring, validating, and normalizing subtitle/transcript data. 

AI-generated subtitles save time initially but create massive cleanup debt afterward. This toolkit targets that cleanup debt.

---

## Validated Pain Points

1. **Caption Cleanup Labor**: Duplicate words, fillers, and messy punctuation.
2. **Broken Subtitle Formatting**: Malformed arrows, index sequencing errors, timing gaps, and whitespace corruption.
3. **Awkward Subtitle Segmentation**: Ugly line breaks and bad phrase spacing.
4. **Vocabulary Correction**: Misspelled technical jargon, brand names, and niche terminology.
5. **YouTube Studio Editing Friction**: Downloading, cleaning, and uploading captions.

---

## Strategic Advantages
* **Local-First**: Complete privacy, speed, and offline reliability.
* **Deterministic Transformations**: Explainable, testable transformations instead of random AI generation.
* **Rapid Iteration**: High-cadence code deployment and testing.

---

## Feature Roadmap

### Stage 1 — Sanitation Core (Current Focus)
* [x] Case-insensitive duplicate word removal
* [x] Resilient timing arrow parsing (supports `-->`, `–>`, `->`)
* [x] Filler word & punctuation correction
* [x] Subtitle validation & syntax repair
* [x] Index sequence numbering correction
* [x] Malformed timestamp recovery
* [x] Line balancing & whitespace normalization
* [x] Non-destructive repair previews (diff mode)

### Stage 2 — Readability Engine
* [x] Phrase-aware line breaking (semantic segmentation)
* [x] Pacing optimization & mobile readability
* [x] Reading speed scoring (WPM metrics)

### Stage 3 — Vocabulary System
* [x] Custom replacement dictionaries (JSON-based vocabulary maps)
* [x] Speaker-specific name & term corrections

### Stage 4 — Workflow Integrations
* [x] YouTube caption download-to-upload pipeline
* [x] Premiere Pro & DaVinci Resolve import optimization
* [x] Batch file directory processing

<!-- 📡 GUIDE COMMENT: Stages 1–4 are done. Do NOT invent a Stage 5 of more cleanup features.
The highest-demand unbuilt items per your own market_research.md AND current 2026 trends are:
  1. Word-level caption splitting (SRT -> per-word timed blocks) + SRT -> ASS karaoke-style export.
     ~85% of short-form video is watched muted; animated word-by-word captions are table stakes
     and competitors charge monthly subscriptions for it. You'd be the free, local-first option.
  2. Speaker color-coding / speaker-tag splitting (ENTRY 010).
But FIRST: distribution & revenue. PyPI publish, Reddit execution, money rail.
Full notes in month1_game/GUIDE_NOTES.md. -->

### Stage 5 — Distribution & Revenue (recommended by GUIDE, not yet started)
* [ ] PyPI publish + GitHub Actions trusted publishing (releases become operator-free)
* [ ] Execute Reddit outreach (templates already written in posts/reddit/)
* [ ] Money rail: GitHub Sponsors / Ko-fi link in README + posts
* [ ] Word-level caption splitter + ASS karaoke export (first revenue-relevant feature)
