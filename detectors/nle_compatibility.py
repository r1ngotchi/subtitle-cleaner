import re

def detect(content: str) -> list[dict]:
    """Scans subtitle blocks for Premiere Pro and DaVinci Resolve compatibility issues."""
    issues = []
    content = content.replace('\r\n', '\n')
    blocks = content.split('\n\n')
    
    current_line = 1
    
    # Check if text contains non-ASCII characters (which require BOM in Resolve)
    has_non_ascii = False
    try:
        content.encode('ascii')
    except UnicodeEncodeError:
        has_non_ascii = True
        
    for idx, block in enumerate(blocks):
        lines = block.split('\n')
        block_len = len(lines)
        if not block.strip():
            current_line += block_len + 1
            continue
            
        timestamp_line_idx = -1
        arrow = None
        for offset, line in enumerate(lines):
            if '-->' in line or '–>' in line or '->' in line:
                timestamp_line_idx = offset
                arrow = '-->' if '-->' in line else ('–>' if '–>' in line else '->')
                break
                
        if timestamp_line_idx != -1:
            timing_line_num = current_line + timestamp_line_idx
            text_lines = lines[timestamp_line_idx + 1:]
            non_empty_text_lines = [l.strip() for l in text_lines if l.strip()]
            
            # 1. Check line count (Premiere/Resolve caption tools support max 2 lines)
            if len(non_empty_text_lines) > 2:
                issues.append({
                    "severity": "HIGH",
                    "type": "nle_compatibility",
                    "line": timing_line_num,
                    "message": f"NLE Import Risk: Block contains {len(non_empty_text_lines)} lines of text. Premiere and Resolve captions support a maximum of 2 lines per block."
                })
                
            # 2. Check line length (Premiere standard safe area is 37 characters)
            for offset_line, line in enumerate(non_empty_text_lines):
                if len(line) > 37:
                    issues.append({
                        "severity": "MEDIUM",
                        "type": "nle_compatibility",
                        "line": timing_line_num + 1 + offset_line,
                        "message": f"NLE Import Risk: Line exceeds 37 characters ({len(line)} chars). Text may wrap awkwardly or get cut off in Premiere's safe area."
                    })
                    
        current_line += block_len + 1
        
    return issues
