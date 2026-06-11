import os
import sys
import glob
import subprocess
from diagnostics import run_diagnostics

def run_regression_tests():
    print("=== Subtitle Cleaner Regression Test Suite ===")
    
    # Locate dataset directory
    # Expected relative to this script: ../../corruption_dataset/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "corruption_dataset"))
    
    if not os.path.exists(dataset_dir):
        print(f"Error: Corruption dataset directory not found at: {dataset_dir}")
        print("Please specify the path using the --dataset option or place it in the sibling directory.")
        sys.exit(1)
        
    print(f"Using dataset directory: {dataset_dir}")
    
    # Discover all srt files
    search_pattern = os.path.join(dataset_dir, "**", "*.srt")
    test_files = glob.glob(search_pattern, recursive=True)
    
    if not test_files:
        print("No test files (.srt) found in the corruption dataset.")
        sys.exit(1)
        
    print(f"Found {len(test_files)} test case(s) to verify.\n")
    
    failed = 0
    passed = 0
    
    for file_path in sorted(test_files):
        case_name = os.path.relpath(file_path, dataset_dir)
        print(f"Running Case: {case_name}")
        
        # 1. Run cleaner against this file
        # We import clean_subtitle_content to run in-memory
        from cleaner import clean_subtitle_content
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
            
        # Clean with fix_overlaps=True to handle timing overlap test cases
        cleaned_content = clean_subtitle_content(
            original_content, 
            fix_overlaps=True,
            segment=True # Enable segmenting to test line balance checks
        )
        
        # 2. Run diagnostics linter on the cleaned output
        findings = run_diagnostics(cleaned_content)
        
        # Filter findings to exclude warnings that are expected or warnings of type nle_compatibility 
        # (long lines may still exceed limits depending on text length even after segmenting)
        filtered_findings = [
            f for f in findings 
            if f['type'] != 'nle_compatibility' # NLE checks are safety warnings, not parser breaking corruptions
        ]
        
        if filtered_findings:
            print(f"  ❌ FAILED: Found {len(filtered_findings)} unresolved issue(s) after cleaning:")
            for issue in filtered_findings:
                print(f"    - [{issue['severity']}] (type: {issue['type']}): {issue['message']}")
            failed += 1
        else:
            print("  ✅ PASSED: Subtitle file sanitized cleanly. 0 critical errors remaining.")
            passed += 1
            
    print("\n=== Regression Test Summary ===")
    print(f"Total: {len(test_files)} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_regression_tests()
