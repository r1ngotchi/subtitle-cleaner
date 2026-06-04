# Subtitle Cleaner & Sanitizer

A fast, local-first utility designed to clean up caption debt. It cleans repeated words, removes fillers, fixes punctuation, and parses/restructures subtitle file formats (`.srt` and `.vtt`).

## Features
- **File Input & Output**: Support for `.srt` and `.vtt` formats (preserves timing blocks and file structures).
- **Resilient Parsing**: Automatically handles various timing arrows (standard `-->`, en-dash `–>`, and short `->`).
- **Deduplication**: Case-insensitive consecutive duplicate word removal (e.g. `We're we're` -> `We're`).
- **Filler Word Stripping**: Cleans common conversational filler words (`um`, `uh`, `like`) along with surrounding punctuation.
- **Local & Offline**: Runs entirely on your local machine with zero third-party API dependencies.

## Usage

### Interactive Text Cleaning
Run without arguments to paste subtitle blocks directly:
```bash
python3 cleaner.py
```

### File Sanitation
Clean a subtitle file and export the output:
```bash
python3 cleaner.py -i input.srt -o output.srt
```

## Running Tests
Run the unit test suite to verify format preservation and text processing rules:
```bash
python3 test_cleaner.py
```

## Project Vision
For our development milestones and planned capabilities, see [ROADMAP.md](ROADMAP.md).