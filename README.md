# Subtitle Cleaner

A local-first subtitle sanitation and diagnostics toolkit.

Current capabilities:
- subtitle cleanup
- duplicate word removal
- filler word cleanup
- SRT/VTT parsing
- corruption diagnostics
- malformed subtitle detection

Current diagnostic categories:
- duplicate indices
- malformed timestamp arrows
- timing overlap detection
- whitespace corruption

Example diagnostic output:

text [HIGH] Broken timestamp arrow [MEDIUM] Duplicate subtitle index [LOW] Excessive whitespace corruption 

Goal:
build trustworthy subtitle sanitation tooling focused on diagnostics, repair safety, and workflow reliability.