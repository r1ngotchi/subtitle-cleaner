import re
import sys
import argparse
import os
import difflib

def apply_vocab_map(text: str, vocab_map: dict) -> str:
    """Applies custom vocabulary mapping using safe word boundary regexes."""
    if not vocab_map:
        return text
    for typo, correction in vocab_map.items():
        escaped_typo = re.escape(typo)
        text = re.sub(r'\b' + escaped_typo + r'\b', correction, text, flags=re.IGNORECASE)
    return text

def clean_text(text: str, vocab_map: dict = None) -> str:
    """Cleans a raw block of text by removing filler words and case-insensitive duplicates."""
    # Normalize curly apostrophes
    text = text.replace("’", "'")
    # Strip HTML/font formatting tags (e.g., <font color="...">text</font> or <i>text</i>)
    text = re.sub(r'<[^>]+>', '', text)
    if vocab_map:
        text = apply_vocab_map(text, vocab_map)
    # Deduplicate case-insensitively (e.g. "We're we're" -> "We're", "the the" -> "the")
    text = re.sub(r'\b([\w\']+)(?:\s+\1\b)+', lambda m: m.group(1), text, flags=re.IGNORECASE)
    
    lines = text.split('\n')
    cleaned_lines = []
    fillers = {'um', 'uh', 'like'}
    
    for line in lines:
        # Tokenize by word boundaries to preserve punctuation and spacing structure
        tokens = re.split(r'(\b[\w\']+\b)', line)
        cleaned_tokens = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if re.match(r'^[\w\']+$', token) and token.lower() in fillers:
                # Remove punctuation/commas attached to the filler word
                if cleaned_tokens:
                    prev_tok = cleaned_tokens[-1]
                    if prev_tok.endswith(','):
                        cleaned_tokens[-1] = prev_tok[:-1]
                    elif prev_tok.endswith(', '):
                        cleaned_tokens[-1] = prev_tok[:-2] + ' '
                if i + 1 < len(tokens):
                    next_tok = tokens[i+1]
                    if next_tok.startswith(','):
                        tokens[i+1] = next_tok[1:]
                i += 1
            else:
                cleaned_tokens.append(token)
                i += 1
                
        new_line = ''.join(cleaned_tokens)
        new_line = re.sub(r' +', ' ', new_line).strip()
        new_line = re.sub(r'^[\s,]+', '', new_line)
        new_line = re.sub(r'[\s,]+$', '', new_line)
        new_line = re.sub(r',\s*,', ',', new_line)
        new_line = re.sub(r'\s+,\s*', ', ', new_line)
        new_line = re.sub(r',(\S)', r', \1', new_line)
        
        if new_line:
            new_line = new_line[0].upper() + new_line[1:]
            cleaned_lines.append(new_line)
            
    return '\n'.join(cleaned_lines)

def normalize_timestamp(time_str: str, is_vtt: bool = False) -> str:
    """Standardizes, pads, and corrects malformed timestamps."""
    time_str = time_str.strip()
    # Replace common wrong separators before milliseconds
    time_str = re.sub(r'[:;,.](\d{1,3})$', lambda m: ('.' if is_vtt else ',') + m.group(1), time_str)
    
    # Match HH:MM:SS (optional milliseconds)
    match = re.match(r'^(\d+):(\d+):(\d+)(?:[.,](\d+))?$', time_str)
    if match:
        h, m, s, ms = match.groups()
        ms = ms or '000'
        ms = f"{ms[:3]:0<3}"
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}" + ('.' if is_vtt else ',') + ms
    
    # Match MM:SS (optional milliseconds)
    match_short = re.match(r'^(\d+):(\d+)(?:[.,](\d+))?$', time_str)
    if match_short:
        m, s, ms = match_short.groups()
        ms = ms or '000'
        ms = f"{ms[:3]:0<3}"
        if is_vtt:
            return f"{int(m):02d}:{int(s):02d}.{ms}"
        else:
            return f"00:{int(m):02d}:{int(s):02d},{ms}"
            
    return time_str

def split_line_semantically(text: str, max_width: int = 40) -> str:
    """Splits a single long line of text into two balanced, grammatically sensible lines."""
    text = text.strip()
    if len(text) <= max_width:
        return text
        
    spaces = [m.start() for m in re.finditer(r'\s+', text)]
    if not spaces:
        return text
        
    middle = len(text) / 2.0
    best_idx = spaces[0]
    best_score = float('inf')
    
    conjunctions = {'and', 'but', 'or', 'because', 'so', 'yet', 'for', 'nor'}
    prepositions = {'to', 'for', 'in', 'on', 'at', 'with', 'by', 'from', 'of', 'about'}
    
    for space_idx in spaces:
        dist = abs(space_idx - middle)
        dist_penalty = (dist / middle) * 2.0
        
        bonus = 0.0
        if space_idx > 0 and text[space_idx - 1] in {',', '.', '?', '!', ';', ':'}:
            bonus += 1.5
            
        next_part = text[space_idx + 1:].strip()
        if next_part:
            next_word = re.split(r'\s+', next_part)[0].lower()
            next_word_clean = re.sub(r'[^\w\']', '', next_word)
            if next_word_clean in conjunctions:
                bonus += 1.2
            elif next_word_clean in prepositions:
                bonus += 0.6
                
        score = dist_penalty - bonus
        if score < best_score:
            best_score = score
            best_idx = space_idx
            
    return text[:best_idx].strip() + '\n' + text[best_idx + 1:].strip()

def clean_subtitle_content(content: str, segment: bool = False, mobile: bool = False, vocab_map: dict = None, nle: str = None, to_format: str = None) -> str:
    """Splits file into blocks, detects timing lines, and cleans text, indices, and timestamps."""
    content = content.replace('\r\n', '\n')
    
    # Preprocess: remove blank lines immediately following a timestamp line
    content = re.sub(r'(\n[^\n]*(?:-->|–>|->)[^\n]*)\n+', r'\1\n', content)
    # Preprocess: remove blank lines between an index number and a timestamp
    content = re.sub(r'(\n\d+)\n+(\d+:\d+:|\d+:\d+\.)', r'\1\n\2', content)
    
    # Clean tabs and trailing whitespace line by line
    lines = [line.replace('\t', ' ').rstrip() for line in content.split('\n')]
    content = '\n'.join(lines)
    
    is_vtt = content.strip().startswith('WEBVTT')
    target_vtt = (to_format.lower() == 'vtt') if to_format else is_vtt
    
    blocks = content.split('\n\n')
    cleaned_blocks = []
    
    if target_vtt and not is_vtt:
        cleaned_blocks.append('WEBVTT')
        
    expected_index = 1
    arrow_pattern = re.compile(r'(-->|–>|->)')
    
    for block in blocks:
        block_stripped = block.strip()
        if not block_stripped:
            continue
            
        lines = block.split('\n')
        timestamp_idx = -1
        for idx, line in enumerate(lines):
            if arrow_pattern.search(line):
                timestamp_idx = idx
                break
                
        if timestamp_idx != -1:
            pre_timestamp = lines[:timestamp_idx]
            timestamp_line = lines[timestamp_idx]
            text_lines = lines[timestamp_idx+1:]
            
            # Normalize timestamp line
            arrow_match = arrow_pattern.search(timestamp_line)
            arrow = arrow_match.group(1)
            parts = timestamp_line.split(arrow)
            if len(parts) == 2:
                start_ts = normalize_timestamp(parts[0], target_vtt)
                end_ts = normalize_timestamp(parts[1], target_vtt)
                timestamp_line = f"{start_ts} --> {end_ts}"
            
            # Correct index sequence
            if to_format:
                if target_vtt:
                    pre_timestamp = []
                else:
                    pre_timestamp = [str(expected_index)]
                    expected_index += 1
            else:
                if pre_timestamp:
                    last_pre = pre_timestamp[-1].strip()
                    if last_pre.isdigit() or not last_pre:
                        pre_timestamp[-1] = str(expected_index)
                        expected_index += 1
                else:
                    if not target_vtt:
                        pre_timestamp = [str(expected_index)]
                        expected_index += 1
            
            cleaned_text = clean_text('\n'.join(text_lines), vocab_map=vocab_map)
            
            if segment or nle == 'premiere':
                if nle == 'premiere':
                    max_width = 37
                else:
                    max_width = 30 if mobile else 40
                split_lines = cleaned_text.split('\n')
                segmented_lines = []
                for line in split_lines:
                    if len(line) > max_width:
                        segmented_lines.append(split_line_semantically(line, max_width))
                    else:
                        segmented_lines.append(line)
                cleaned_text = '\n'.join(segmented_lines)
            
            reconstructed_lines = pre_timestamp + [timestamp_line]
            if cleaned_text:
                reconstructed_lines.append(cleaned_text)
            
            cleaned_blocks.append('\n'.join(reconstructed_lines))
        else:
            # If target is VTT and source is VTT, preserve metadata
            if target_vtt and is_vtt:
                # Skip duplicate WEBVTT prepends
                if block_stripped == 'WEBVTT' and len(cleaned_blocks) > 0 and cleaned_blocks[0] == 'WEBVTT':
                    continue
                cleaned_blocks.append(block)
            # If target is SRT, skip VTT headers/metadata blocks
            
    return '\n\n'.join(cleaned_blocks)

def print_preview(original: str, cleaned: str):
    """Compares original and cleaned content line-by-line and prints a colored unified diff."""
    diff_lines = list(difflib.unified_diff(
        original.replace('\r\n', '\n').splitlines(),
        cleaned.replace('\r\n', '\n').splitlines(),
        fromfile='Original',
        tofile='Cleaned',
        lineterm=''
    ))
    
    if not diff_lines:
        print("No issues detected. Subtitle file is already clean.")
        return
        
    print("=== Subtitle Repair Preview ===")
    print("Showing proposed changes (non-destructive review):\n")
    for line in diff_lines:
        if line.startswith('---') or line.startswith('+++'):
            continue
        elif line.startswith('-'):
            print(f"\033[91m{line}\033[0m" if sys.stdout.isatty() else line)
        elif line.startswith('+'):
            print(f"\033[92m{line}\033[0m" if sys.stdout.isatty() else line)
        elif line.startswith('@@'):
            print(f"\033[36m{line}\033[0m" if sys.stdout.isatty() else line)
        else:
            print(line)

def main():
    parser = argparse.ArgumentParser(description="Subtitle Cleaner - Removes duplicates & filler words.")
    parser.add_argument("-i", "--input", help="Path to input subtitle/text file. If omitted, reads from interactive prompt.")
    parser.add_argument("-o", "--output", help="Path to save the cleaned file. If omitted, prints to standard output.")
    parser.add_argument("-p", "--preview", action="store_true", help="Generate a non-destructive preview of repairs (diff) without saving.")
    parser.add_argument("-s", "--segment", action="store_true", help="Automatically segment long subtitle lines semantically based on grammatical cues.")
    parser.add_argument("-m", "--mobile", action="store_true", help="Optimize subtitle line breaking width for mobile/vertical screens (max width: 30 chars).")
    parser.add_argument("-v", "--vocab", help="Path to JSON-based vocabulary mapping file for custom search-and-replace corrections.")
    parser.add_argument("--nle", choices=["premiere", "resolve"], help="Optimize output explicitly for Premiere Pro or DaVinci Resolve compatibility.")
    parser.add_argument("-f", "--format", choices=["srt", "vtt"], help="Force output subtitle format conversion (srt or vtt).")
    
    args = parser.parse_args()
    
    vocab_map = None
    if args.vocab:
        if not os.path.exists(args.vocab):
            print(f"Error: Vocab file not found: {args.vocab}", file=sys.stderr)
            sys.exit(1)
        import json
        with open(args.vocab, 'r', encoding='utf-8') as f:
            try:
                vocab_map = json.load(f)
            except Exception as e:
                print(f"Error: Failed to parse vocab JSON: {e}", file=sys.stderr)
                sys.exit(1)
    
    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: Path not found: {args.input}", file=sys.stderr)
            sys.exit(1)
            
        if os.path.isdir(args.input):
            # Batch directory processing
            print(f"Batch processing directory: {args.input}")
            files_to_process = []
            for root, dirs, files in os.walk(args.input):
                for file in files:
                    if file.lower().endswith(('.srt', '.vtt')):
                        files_to_process.append(os.path.join(root, file))
                        
            if not files_to_process:
                print("No .srt or .vtt subtitle files found in the directory.")
                sys.exit(0)
                
            print(f"Found {len(files_to_process)} file(s) to process.\n")
            
            for file_path in files_to_process:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                cleaned = clean_subtitle_content(content, segment=args.segment, mobile=args.mobile, vocab_map=vocab_map, nle=args.nle, to_format=args.format)
                
                if args.preview:
                    print(f"\n--- Preview: {file_path} ---")
                    print_preview(content, cleaned)
                    continue
                    
                # Determine output path
                if args.output:
                    rel_path = os.path.relpath(file_path, args.input)
                    if args.format:
                        rel_path = os.path.splitext(rel_path)[0] + f".{args.format}"
                    out_path = os.path.join(args.output, rel_path)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                else:
                    base, ext = os.path.splitext(file_path)
                    target_ext = f".{args.format}" if args.format else ext
                    out_path = f"{base}_cleaned{target_ext}"
                    
                encoding = "utf-8-sig" if args.nle == "resolve" else "utf-8"
                with open(out_path, "w", encoding=encoding) as f:
                    f.write(cleaned)
                    if not cleaned.endswith('\n'):
                        f.write('\n')
                print(f"Cleaned and saved: {out_path}")
            sys.exit(0)
            
        else:
            # Single file processing
            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()
                
            is_sub = "-->" in content or "–>" in content or "->" in content
            if is_sub:
                cleaned = clean_subtitle_content(content, segment=args.segment, mobile=args.mobile, vocab_map=vocab_map, nle=args.nle, to_format=args.format)
            else:
                cleaned = clean_text(content, vocab_map=vocab_map)
                
            if args.preview:
                print_preview(content, cleaned)
                sys.exit(0)
                
            if args.output:
                if os.path.isdir(args.output):
                    basename = os.path.basename(args.input)
                    if args.format:
                        basename = os.path.splitext(basename)[0] + f".{args.format}"
                    out_path = os.path.join(args.output, basename)
                else:
                    out_path = args.output
                    if args.format and not out_path.endswith(f".{args.format}"):
                        out_path = os.path.splitext(out_path)[0] + f".{args.format}"
                encoding = "utf-8-sig" if args.nle == "resolve" else "utf-8"
                with open(out_path, "w", encoding=encoding) as f:
                    f.write(cleaned)
                    if not cleaned.endswith('\n'):
                        f.write('\n')
                print(f"Successfully cleaned and saved to {out_path}")
            else:
                print(cleaned)
    else:
        # Fall back to interactive CLI prompt
        print("=== Subtitle Cleaner v0.2 ===")
        print("Paste subtitle text (press Ctrl+D on Unix or Ctrl+Z on Windows + Enter to finish):")
        try:
            content = sys.stdin.read()
        except KeyboardInterrupt:
            sys.exit(0)
            
        if not content.strip():
            sys.exit(0)
            
        is_sub = "-->" in content or "–>" in content or "->" in content
        if is_sub:
            cleaned = clean_subtitle_content(content, segment=args.segment, mobile=args.mobile, vocab_map=vocab_map, nle=args.nle, to_format=args.format)
        else:
            cleaned = clean_text(content, vocab_map=vocab_map)
            
        if args.preview:
            print_preview(content, cleaned)
            sys.exit(0)
            
        print("\n=== Cleaned Output ===\n")
        print(cleaned)

if __name__ == "__main__":
    main()