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
* [ ] Subtitle validation & syntax repair
* [ ] Index sequence numbering correction
* [ ] Malformed timestamp recovery
* [ ] Line balancing & whitespace normalization

### Stage 2 — Readability Engine
* [ ] Phrase-aware line breaking (semantic segmentation)
* [ ] Pacing optimization & mobile readability
* [ ] Reading speed scoring (WPM metrics)

### Stage 3 — Vocabulary System
* [ ] Custom replacement dictionaries (JSON-based vocabulary maps)
* [ ] Speaker-specific name & term corrections

### Stage 4 — Workflow Integrations
* [ ] YouTube caption download-to-upload pipeline
* [ ] Premiere Pro & DaVinci Resolve import optimization
* [ ] Batch file directory processing
