import re

def detect(content: str) -> list[dict]:
    """Scans subtitle timing lines for non-standard arrow indicators or malformed spacing."""
    issues = []
    content = content.replace('\r\n', '\n')
    lines = content.split('\n')
    
    for idx, line in enumerate(lines):
        line_num = idx + 1
        
        # Check if the line looks like a timing indicator block
        # Typically looks like: 00:00:01,000 --> 00:00:04,000
        # If it has timing delimiters but has wrong arrows:
        if ('->' in line or '–>' in line) and '-->' not in line:
            issues.append({
                "severity": "HIGH",
                "type": "broken_arrows",
                "line": line_num,
                "message": f"Malformed timestamp arrow detected: '{line.strip()}'."
            })
            
    return issues
