import importlib
import os
import sys

# Central list of active detectors
DETECTOR_MODULES = [
    "detectors.duplicate_indices",
    "detectors.broken_arrows",
    "detectors.timing_overlap",
    "detectors.whitespace_corruption",
    "detectors.reading_speed",
    "detectors.nle_compatibility"
]

def run_diagnostics(content: str) -> list[dict]:
    """Runs all registered detectors against subtitle content and compiles issues."""
    issues = []
    
    # Ensure local path is available for dynamic loading if needed
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    for module_name in DETECTOR_MODULES:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "detect"):
                issues.extend(module.detect(content))
        except Exception as e:
            # Output warning internally if a detector fails to run
            print(f"Warning: Failed to execute detector {module_name}: {e}", file=sys.stderr)
            
    return issues

if __name__ == "__main__":
    # Standard CLI test loop
    import argparse
    parser = argparse.ArgumentParser(description="Subtitle Diagnostics Runner")
    parser.add_argument("file", help="Path to subtitle file to scan")
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
        
    with open(args.file, "r", encoding="utf-8") as f:
        data = f.read()
        
    findings = run_diagnostics(data)
    print(f"--- Diagnostic Report: {args.file} ---")
    print(f"Found {len(findings)} issue(s).\n")
    for issue in findings:
        print(f"[{issue['severity']}] Line {issue['line']} ({issue['type']}): {issue['message']}")
