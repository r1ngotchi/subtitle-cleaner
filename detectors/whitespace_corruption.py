def detect(content: str) -> list[dict]:
    """Scans subtitle lines for whitespace anomalies such as tabs, trailing whitespace, or double blank lines."""
    issues = []
    content = content.replace('\r\n', '\n')
    lines = content.split('\n')
    
    # Track empty lines sequentially
    consecutive_newlines = 0
    
    for idx, line in enumerate(lines):
        line_num = idx + 1
        
        # Check consecutive blank lines
        if not line.strip():
            consecutive_newlines += 1
            if consecutive_newlines > 1:
                issues.append({
                    "severity": "LOW",
                    "type": "whitespace_corruption",
                    "line": line_num,
                    "message": "Consecutive empty lines detected."
                })
        else:
            consecutive_newlines = 0
            
        # Check tabs
        if '\t' in line:
            issues.append({
                "severity": "LOW",
                "type": "whitespace_corruption",
                "line": line_num,
                "message": "Tab character detected (standard formatting uses spaces)."
            })
            
        # Check trailing whitespace
        if line.rstrip() != line:
            issues.append({
                "severity": "LOW",
                "type": "whitespace_corruption",
                "line": line_num,
                "message": "Trailing whitespace detected at end of line."
            })
            
    return issues
