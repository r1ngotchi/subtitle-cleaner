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

## Submit Broken Subtitle Files

If you encounter:

* malformed subtitle exports
* broken SRT/VTT files
* timing corruption
* import failures
* subtitle formatting issues

please submit a GitHub issue with the subtitle file attached.

The project is currently building a structured corruption dataset to improve subtitle diagnostics and repair reliability.