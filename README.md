# subtitle-cleaner

> **A local-first Python CLI toolkit for sanitizing, repairing, and optimizing AI-generated subtitle files.**

AI transcription tools (Whisper, CapCut, Premiere's auto-transcribe) save time up front — but the cleanup afterward is brutal. Stuttered words, broken import syntax, filler noise, and ugly line breaks pile up fast.

`subtitle-cleaner` runs **entirely on your machine** with no cloud dependencies, no privacy risk, and no subscription.

---

## ✨ Features

| Feature | Flag | Description |
|---------|------|-------------|
| **Duplicate word removal** | *(default)* | Case-insensitively removes stutters (`"We're we're"` → `"We're"`) |
| **Filler word stripping** | *(default)* | Removes `um`, `uh`, `like` without breaking timings |
| **HTML/font tag stripping** | *(default)* | Cleans embedded `<font>`, `<i>`, `<b>` tags from SRT/VTT |
| **Arrow & timestamp repair** | *(default)* | Normalizes unicode arrows (`–>`, `->`) to standard `-->` |
| **Index re-sequencing** | *(default)* | Fixes out-of-order subtitle block indices starting from 1 |
| **Timestamp normalization** | *(default)* | Pads and corrects malformed `HH:MM:SS,mmm` timestamps |
| **Repair preview (diff)** | `--preview` / `-p` | Non-destructive diff of proposed changes before saving |
| **Semantic line breaking** | `--segment` / `-s` | Splits long lines at grammatical boundaries (not character counts) |
| **Mobile formatting** | `--mobile` / `-m` | 30-character line width for 9:16 vertical video (TikTok/Shorts/Reels) |
| **Custom vocabulary map** | `--vocab vocab.json` | JSON-based find-and-replace for brand names, jargon, speaker names |
| **NLE optimization** | `--nle premiere\|resolve` | Premiere Pro (37-char limit, 2-line max) and Resolve (UTF-8 BOM) modes |
| **Batch processing** | `-i /folder/ -o /out/` | Recursively processes entire directories of `.srt`/`.vtt` files |
| **Format conversion** | `--format srt\|vtt\|ass` / `-f srt\|vtt\|ass` | Convert between SRT, VTT, and ASS formats (converts timestamps & styles) |
| **Word-level splitting** | `--word-split` / `-w` | Splits blocks into single-word timed subtitle blocks (proportionally distributed duration) |
| **Karaoke style export** | `--karaoke` / `-k` | Exports to ASS format with highlighting `{\k}` centisecond timings |
| **YouTube caption sync** | `youtube_sync.py` | Downloads, cleans, and saves captions from any YouTube URL |

---

## 🚀 Installation

```bash
# Install directly from GitHub
pip install git+https://github.com/r1ngotchi/subtitle-cleaner.git

# Or clone and install in editable mode for development
git clone https://github.com/r1ngotchi/subtitle-cleaner
cd subtitle-cleaner
pip install -e .
```

## 💻 Quick Start

Once installed, the toolkit provides three convenient CLI commands:

```bash
# Preview what would change (non-destructive)
subtitle-cleaner -i messy.srt --preview

# Clean and save output
subtitle-cleaner -i messy.srt -o clean.srt

# Clean for Premiere Pro import (37-char line limit, 2-line max)
subtitle-cleaner -i messy.srt -o clean.srt --nle premiere

# Clean for DaVinci Resolve (UTF-8 BOM encoding)
subtitle-cleaner -i messy.srt -o clean.srt --nle resolve

# Semantic line breaking + mobile formatting
subtitle-cleaner -i messy.srt -o clean.srt --segment --mobile

# Apply custom vocabulary corrections
subtitle-cleaner -i messy.srt -o clean.srt --vocab my_vocab.json

# Batch process an entire folder
subtitle-cleaner -i ./subtitles/ -o ./cleaned/

# Convert SRT to VTT (strips indices, normalizes dots)
subtitle-cleaner -i input.srt -o output.vtt -f vtt

# Convert VTT to SRT (restores sequential indices, normalizes commas)
subtitle-cleaner -i input.vtt -o output.srt -f srt

# Split subtitles into single-word blocks (e.g. for vertical video captions)
subtitle-cleaner -i input.srt -o output.srt -w

# Convert to ASS format with karaoke highlighting (for animated captions)
subtitle-cleaner -i input.srt -o output.ass -k

# Download and clean YouTube captions directly
subtitle-youtube-sync https://www.youtube.com/watch?v=VIDEO_ID -o output.vtt
```

---

## 📋 Before / After Example

**Input (`messy.srt`):**
```
1
00:00:01,000 -> 00:00:04,000
Yeah, we're we're going to like, um, build this.

1
00:00:04,100 ---> 00:00:06,000
Like, uh, <font color="#ff0000">absolutely.</font>
```

**Output after `python cleaner.py -i messy.srt`:**
```
1
00:00:01,000 --> 00:00:04,000
Yeah, we're going to build this.

2
00:00:04,100 --> 00:00:06,000
Absolutely.
```

---

## 📦 Custom Vocabulary Map (`--vocab`)

Create a `vocab.json` file mapping AI mistranscriptions to their correct forms:

```json
{
  "open eye": "OpenAI",
  "adobe premiere pro": "Adobe Premiere Pro",
  "da vinci resolve": "DaVinci Resolve"
}
```

Then run: `python cleaner.py -i messy.srt -o clean.srt --vocab vocab.json`

---

## 🔬 Diagnostics

Run the linter to get a full report of issues before cleaning:

```bash
subtitle-diagnostics messy.srt
```

The linter checks for:
- **Reading speed** — flags blocks with dangerously high CPS (characters per second)
- **NLE compatibility** — warns about 3+ line blocks and lines >37 chars (Premiere crash risk)
- **Timing overlaps** — detects blocks where end time > next block's start time
- **Whitespace corruption** — tabs, trailing spaces, CRLF issues

---

## ⚙️ YouTube Caption Sync

```bash
subtitle-youtube-sync https://www.youtube.com/watch?v=VIDEO_ID -o captions.vtt
```

Downloads auto-generated or manually uploaded captions, cleans them, and saves a polished file ready for upload or NLE import.

---

## 🧪 Tests

### Unit Tests
Verify individual module features and parser stability:
```bash
python -m unittest test_cleaner.py
# Expected: 19 tests, all passing
```

### Regression Tests
Test the cleaner automatically against all collected real-world corruptions in the dataset:
```bash
subtitle-regression
# Expected: Runs and passes all dataset test cases with 0 critical errors remaining
```

---

## 📁 Project Structure

```
subtitle-cleaner/
├── cleaner.py          # Core CLI tool
├── diagnostics.py      # Linting & validation engine
├── youtube_sync.py     # YouTube caption downloader-cleaner
├── detectors/          # Modular lint checkers
│   ├── reading_speed.py
│   ├── nle_compatibility.py
│   └── ...
├── sample_input.srt    # Test fixture
├── sample_vocab.json   # Example vocabulary map
└── test_cleaner.py     # 15 unit + integration tests
```

---

## 🤝 Contributing

Found a subtitle file that breaks the parser? [Submit an issue](https://github.com/r1ngotchi/subtitle-cleaner/issues) and attach the file — we're building a structured corruption dataset to improve repair reliability.

Pull requests welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## ☕ Support & Funding

If `subtitle-cleaner` saves you hours of manual editing, consider supporting the project:
- **Ko-fi**: [Support r1ngotchi on Ko-fi](https://ko-fi.com/r1ngotchi)
- **GitHub Sponsors**: [Sponsor r1ngotchi](https://github.com/sponsors/r1ngotchi)

---

## 📄 License

MIT — free to use, modify, and distribute.