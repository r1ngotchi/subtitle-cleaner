import re

def detect(content: str) -> list[dict]:
    """Scans subtitle blocks for indexing issues (duplicates, skips, non-sequential numbering)."""
    issues = []
    content = content.replace('\r\n', '\n')
    blocks = content.split('\n\n')
    
    expected_index = 1
    # Maintain tracking of block start lines in the original content
    current_line = 1
    
    for block in blocks:
        lines = block.split('\n')
        block_len = len(lines)
        if not block.strip():
            current_line += block_len + 1
            continue
            
        # The index number is typically the first line of the block
        index_line = lines[0].strip()
        
        # Check if the block has a timestamp line
        has_timestamp = any('-->' in line or '–>' in line or '->' in line for line in lines)
        if has_timestamp and index_line.isdigit():
            actual_index = int(index_line)
            
            if actual_index != expected_index:
                if actual_index < expected_index:
                    issues.append({
                        "severity": "MEDIUM",
                        "type": "duplicate_indices",
                        "line": current_line,
                        "message": f"Duplicate or non-sequential index number: found {actual_index}, expected {expected_index}."
                    })
                else:
                    issues.append({
                        "severity": "MEDIUM",
                        "type": "duplicate_indices",
                        "line": current_line,
                        "message": f"Skipped index numbering: found {actual_index}, expected {expected_index}."
                    })
            
            # Update expected index to continue sequentially
            expected_index = actual_index + 1
            
        current_line += len(lines) + 1
        
    return issues
