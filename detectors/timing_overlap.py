import re

def parse_time_to_ms(time_str: str) -> int:
    """Parses subtitle timing strings (HH:MM:SS,mmm or HH:MM:SS.mmm) into milliseconds."""
    # Normalize separators
    time_str = time_str.strip().replace(',', '.')
    parts = time_str.split('.')
    hms = parts[0].split(':')
    
    hours = int(hms[0])
    minutes = int(hms[1])
    seconds = int(hms[2])
    ms = int(parts[1]) if len(parts) > 1 else 0
    
    return ((hours * 3600 + minutes * 60 + seconds) * 1000) + ms

def detect(content: str) -> list[dict]:
    """Scans timing intervals for overlaps, negative ranges, or impossible timing bounds."""
    issues = []
    content = content.replace('\r\n', '\n')
    blocks = content.split('\n\n')
    
    # Store tuples of (start_ms, end_ms, line_num, block_index)
    intervals = []
    current_line = 1
    
    for idx, block in enumerate(blocks):
        lines = block.split('\n')
        block_len = len(lines)
        if not block.strip():
            current_line += block_len + 1
            continue
            
        # Find timing line
        for offset, line in enumerate(lines):
            # Look for timestamp line
            if '-->' in line or '–>' in line or '->' in line:
                arrow = '-->' if '-->' in line else ('–>' if '–>' in line else '->')
                parts = line.split(arrow)
                if len(parts) == 2:
                    try:
                        start_ms = parse_time_to_ms(parts[0])
                        end_ms = parse_time_to_ms(parts[1])
                        timing_line_num = current_line + offset
                        
                        # Check negative duration
                        if end_ms < start_ms:
                            issues.append({
                                "severity": "HIGH",
                                "type": "timing_overlap",
                                "line": timing_line_num,
                                "message": f"Negative duration detected: start ({parts[0].strip()}) is after end ({parts[1].strip()})."
                            })
                            
                        intervals.append((start_ms, end_ms, timing_line_num, idx + 1))
                    except Exception:
                        # Parsing error handled by other detectors
                        pass
                break
                
        current_line += block_len + 1

    # Check overlaps sequentially
    for i in range(len(intervals) - 1):
        curr_start, curr_end, curr_line, curr_idx = intervals[i]
        next_start, next_end, next_line, next_idx = intervals[i+1]
        
        if curr_end > next_start:
            issues.append({
                "severity": "MEDIUM",
                "type": "timing_overlap",
                "line": next_line,
                "message": f"Timing overlap: block {next_idx} starts before block {curr_idx} ends."
            })
            
    return issues
