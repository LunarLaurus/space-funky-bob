# Task ECHO-005: Tutorial Creation

**Squad:** Echo (Documentation & Integration)  
**Priority:** P1 (High)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Create comprehensive step-by-step tutorials that guide new users through common workflows, enabling them to become productive with the toolkit in under 30 minutes.

---

## Context

New users face a learning curve when starting ROM analysis. Tutorials provide:
- Guided walkthroughs of common tasks
- Expected outputs at each step
- Troubleshooting tips
- Best practices

Well-written tutorials reduce support burden and improve user success rates.

---

## Acceptance Criteria

- [ ] Tutorial 1: Getting Started (15 min)
- [ ] Tutorial 2: Finding Compressed Blocks (20 min)
- [ ] Tutorial 3: Graphics Extraction & Rendering (25 min)
- [ ] Tutorial 4: Level Editing Workflow (30 min)
- [ ] Tutorial 5: Ghidra/IDA Integration (20 min)
- [ ] Video supplements: Optional screen recordings
- [ ] Exercise files: Sample ROMs and expected outputs

---

## Technical Notes

### Tutorial Structure

Each tutorial follows this template:

```markdown
# Tutorial X: [Title]

**Duration:** X minutes  
**Difficulty:** Beginner/Intermediate/Advanced  
**Prerequisites:** [list]

## Overview
What you'll learn and why it matters.

## Setup
Files needed, environment setup.

## Step 1: [Action]
Detailed instructions with screenshots.

## Step 2: [Action]
...

## Expected Output
What you should see/have at the end.

## Troubleshooting
Common issues and solutions.

## Next Steps
Where to go from here.
```

### Tutorial Outlines

**Tutorial 1: Getting Started (15 min)**
- Install Python
- Download toolkit
- Run test suite
- Scan a sample ROM
- View results

**Tutorial 2: Finding Compressed Blocks (20 min)**
- Understand LZ77 format
- Run scanner with default settings
- Interpret candidates.json
- Decompress a block
- Validate against known block

**Tutorial 3: Graphics Extraction (25 min)**
- Locate graphics data
- Extract graphics blob
- Render as 2bpp/4bpp/8bpp
- Apply palettes
- Generate sprite sheet

**Tutorial 4: Level Editing (30 min)**
- Extract level tilemap
- View tilemap visually
- Modify tiles
- Inject modified tilemap
- Test in emulator

**Tutorial 5: Ghidra/IDA Integration (20 min)**
- Export ROM map
- Import to Ghidra/IDA
- Navigate annotated ROM
- Use analysis results

---

## Files to Modify

- `docs/tutorials/` — New tutorial directory
- `docs/tutorials/01_getting_started.md`
- `docs/tutorials/02_finding_compressed_blocks.md`
- `docs/tutorials/03_graphics_extraction.md`
- `docs/tutorials/04_level_editing.md`
- `docs/tutorials/05_ghidra_ida_integration.md`
- `README.md` — Add tutorial links

---

## Dependencies

- **Blocks:** None
- **Blocked by:** All squad tasks (need features to document)

---

## Test Plan

1. Have new user follow each tutorial
2. Time completion for each
3. Collect feedback on clarity
4. Update based on feedback
5. Verify all commands work

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — Tutorial creation complete
  - Created `docs/tutorials/` directory with 5 comprehensive tutorials:
    - Tutorial 1: Getting Started (15 min) — Setup, test suite, first analysis
    - Tutorial 2: Finding Compressed Blocks (20 min) — LZ77 format, scanner usage, validation
    - Tutorial 3: Graphics Extraction (25 min) — SNES formats, rendering, palettes, sprite sheets
    - Tutorial 4: Level Editing (30 min) — Tilemap structure, extraction, editing, injection
    - Tutorial 5: Ghidra/IDA Integration (20 min) — Import scripts, navigation, analysis tips
  - All tutorials include:
    - Step-by-step instructions
    - Expected outputs
    - Troubleshooting sections
    - Next steps guidance
  - All acceptance criteria met
