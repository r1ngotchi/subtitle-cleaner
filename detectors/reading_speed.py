import re
from detectors.timing_overlap import parse_time_to_ms

# Industry standard readability thresholds
MAX_CPS = 20.0  # Max characters per second (Netflix standard is 20 CPS)

def detect(content: str) -> list[dict]:
    """Scans subtitle blocks for excessive reading speed (characters per second)."""
    issues = []
    content = content.replace('\r\n', '\n')
    blocks = content.split('\n\n')
    
    current_line = 1
    
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
            parts = lines[timestamp_line_idx].split(arrow)
            if len(parts) == 2:
                try:
                    start_ms = parse_time_to_ms(parts[0])
                    end_ms = parse_time_to_ms(parts[1])
                    duration_s = (end_ms - start_ms) / 1000.0
                    
                    # Get text content below the timestamp
                    text_lines = lines[timestamp_line_idx + 1:]
                    text_content = " ".join(text_lines).strip()
                    
                    # Remove multiple spaces and calculate length (excluding spaces)
                    clean_text = re.sub(r'\s+', '', text_content)
                    char_count = len(clean_text)
                    
                    if duration_s > 0 and char_count > 0:
                        cps = char_count / duration_s
                        if cps > MAX_CPS:
                            severity = "HIGH" if cps > 30.0 else "MEDIUM"
                            issues.append({
                                "severity": severity,
                                "type": "reading_speed",
                                "line": timing_line_num,
                                "message": f"High reading speed: {cps:.1f} characters/sec (Max recommended: {MAX_CPS:.1f} CPS). Block has {char_count} chars in {duration_s:.2f}s."
                            })
                        
                        # Mobile pacing checks
                        non_empty_text_lines = [l for l in text_lines if l.strip()]
                        if len(non_empty_text_lines) >= 2 and duration_s < 1.5:
                            issues.append({
                                "severity": "MEDIUM",
                                "type": "reading_speed",
                                "line": timing_line_num,
                                "message": f"Pacing issue (mobile readability): Block contains {len(non_empty_text_lines)} lines of text but duration is only {duration_s:.2f}s (Min recommended for 2 lines: 1.50s)."
                            })
                except Exception:
                    pass
                    
        current_line += block_len + 1
        
    return issues
