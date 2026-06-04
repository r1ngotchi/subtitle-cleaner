import re
import sys
import argparse
import os

def clean_text(text: str) -> str:
    """Cleans a raw block of text by removing filler words and case-insensitive duplicates."""
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

def clean_subtitle_content(content: str) -> str:
    """Splits file into blocks, detects timing lines, and cleans only text segments."""
    content = content.replace('\r\n', '\n')
    blocks = content.split('\n\n')
    cleaned_blocks = []
    
    for block in blocks:
        block_stripped = block.strip()
        if not block_stripped:
            continue
            
        lines = block.split('\n')
        timestamp_idx = -1
        for idx, line in enumerate(lines):
            if '-->' in line:
                timestamp_idx = idx
                break
                
        if timestamp_idx != -1:
            pre_timestamp = lines[:timestamp_idx]
            timestamp_line = lines[timestamp_idx]
            text_lines = lines[timestamp_idx+1:]
            
            cleaned_text = clean_text('\n'.join(text_lines))
            
            reconstructed_lines = pre_timestamp + [timestamp_line]
            if cleaned_text:
                reconstructed_lines.append(cleaned_text)
            
            cleaned_blocks.append('\n'.join(reconstructed_lines))
        else:
            # Preserve VTT headers or metadata blocks
            cleaned_blocks.append(block)
            
    return '\n\n'.join(cleaned_blocks)

def main():
    parser = argparse.ArgumentParser(description="Subtitle Cleaner - Removes duplicates & filler words.")
    parser.add_argument("-i", "--input", help="Path to input subtitle/text file. If omitted, reads from interactive prompt.")
    parser.add_argument("-o", "--output", help="Path to save the cleaned file. If omitted, prints to standard output.")
    
    args = parser.parse_args()
    
    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
            
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Detect if it's a subtitle file or standard text
        is_sub = "-->" in content
        if is_sub:
            cleaned = clean_subtitle_content(content)
        else:
            cleaned = clean_text(content)
            
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(cleaned)
                if not cleaned.endswith('\n'):
                    f.write('\n')
            print(f"Successfully cleaned and saved to {args.output}")
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
            
        is_sub = "-->" in content
        if is_sub:
            cleaned = clean_subtitle_content(content)
        else:
            cleaned = clean_text(content)
            
        print("\n=== Cleaned Output ===\n")
        print(cleaned)

if __name__ == "__main__":
    main()