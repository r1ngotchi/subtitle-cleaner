# Subtitle Cleaner & Sanitizer

A fast, local-first utility designed to clean up caption debt. It cleans repeated words, removes fillers, fixes punctuation, parses/restructures subtitle file formats (`.srt` and `.vtt`), and scans for timing and formatting corruption.

## Features
- **File Input & Output**: Support for `.srt` and `.vtt` formats (preserves timing blocks and file structures).
- **Resilient Parsing**: Automatically handles various timing arrows (standard `-->`, en-dash `–>`, and short `->`).
- **Deduplication**: Case-insensitive consecutive duplicate word removal (e.g. `We're we're` -> `We're`).
- **Filler Word Stripping**: Cleans common conversational filler words (`um`, `uh`, `like`) along with surrounding punctuation.
- **Diagnostic Linter**: Detects and reports index numbering errors, broken timestamp indicators, timing overlaps, and whitespace corruption.
- **Local & Offline**: Runs entirely on your local machine with zero third-party API dependencies.

## Usage

### Subtitle Diagnostics (Linter)
Scan a subtitle file for timing and formatting errors without modifying it:
```bash
python3 diagnostics.py demo_corrupt.srt
```

Output Example:
```text
--- Diagnostic Report: demo_corrupt.srt ---
Found 8 issue(s).

[MEDIUM] Line 5 (duplicate_indices): Duplicate or non-sequential index number: found 1, expected 2.
[MEDIUM] Line 9 (duplicate_indices): Skipped index numbering: found 3, expected 2.
[HIGH] Line 2 (broken_arrows): Malformed timestamp arrow detected: '00:00:01,000 -> 00:00:04,000'.
[HIGH] Line 6 (broken_arrows): Malformed timestamp arrow detected: '00:00:03,500 –> 00:00:05,000'.
[HIGH] Line 10 (broken_arrows): Malformed timestamp arrow detected: '00:00:05,500 –> 00:00:08,000'.
[MEDIUM] Line 6 (timing_overlap): Timing overlap: block 2 starts before block 1 ends.
[LOW] Line 3 (whitespace_corruption): Trailing whitespace detected at end of line.
[LOW] Line 11 (whitespace_corruption): Tab character detected (standard formatting uses spaces).
```

### File Sanitation (Cleaner)
Clean a subtitle file and export the output:
```bash
python3 cleaner.py -i input.srt -o output.srt
```

### Interactive Text Cleaning
Run without arguments to paste subtitle blocks directly:
```bash
python3 cleaner.py
```

## Running Tests
Run the unit test suite to verify format preservation and text processing rules:
```bash
python3 test_cleaner.py
```

## Project Vision
For our development milestones and planned capabilities, see [ROADMAP.md](ROADMAP.md).