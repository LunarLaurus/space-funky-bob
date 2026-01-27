# Sprint Planning - B.O.B. ROM Analysis Toolkit

## Sprint 0: Foundation (COMPLETED)
**Duration**: Initial development  
**Goal**: Establish core functionality and MVP deliverables

### Stories Completed
- ✅ **CORE-001**: Implement B.O.B. LZ77 decoder with error handling
  - Acceptance: Passes 5+ unit tests including overlapping copies
  - Status: DONE - All tests passing

- ✅ **CORE-002**: Create ROM scanner for compressed block detection
  - Acceptance: Identifies compressed blocks via entropy heuristics
  - Status: DONE - Entropy scanning, decompression validation implemented

- ✅ **CORE-003**: Build code/data classifier with 65816 analysis
  - Acceptance: Classifies regions with >80% accuracy on test ROM
  - Status: DONE - Opcode density, entropy, vector analysis complete

- ✅ **CORE-004**: Generate JSON outputs for automation
  - Acceptance: Valid JSON with all required fields
  - Status: DONE - candidates.json and rom_map.json schemas defined

- ✅ **CORE-005**: Write Ghidra import documentation
  - Acceptance: Step-by-step guide with Python script example
  - Status: DONE - ghidra_import.txt with manual and scripted methods

- ✅ **DOC-001**: Create comprehensive README
  - Acceptance: Quick start, troubleshooting, examples included
  - Status: DONE - Full README with usage examples

- ✅ **TEST-001**: Validate against known B.O.B. block at 0x1AD34
  - Acceptance: Correctly decompresses to 0x822 bytes
  - Status: DONE - validate_known_block.py script created

### Metrics
- **Story Points Completed**: 21/21
- **Velocity**: 21 points (baseline sprint)
- **Bugs Found**: 0
- **Test Coverage**: Core functions covered

---

## Sprint 1: Enhancement & Validation (CURRENT)
**Duration**: 2 weeks  
**Goal**: Improve accuracy, add HTML visualization, expand testing

### Planned Stories

#### High Priority
- 🔄 **VIZ-001**: Complete HTML visualization implementation
  - **Points**: 5
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Interactive ROM map with color-coded regions
    - Hover tooltips showing region details
    - Responsive design, works in all modern browsers
    - Clickable regions that link to decompressed files
  - **Status**: IN PROGRESS (skeleton exists, needs refinement)

- ⬜ **TEST-002**: Expand test suite with edge cases
  - **Points**: 3
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Test truncated compressed streams
    - Test ROMs with/without headers
    - Test HiROM detection (if sample available)
    - Test invalid distance/length combinations
  - **Status**: NOT STARTED

- ⬜ **DOC-002**: Create API documentation
  - **Points**: 2
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Sphinx or similar documentation format
    - All public functions documented
    - Example code snippets for common use cases
  - **Status**: NOT STARTED

#### Medium Priority
- ⬜ **SCAN-001**: Improve compressed block detection accuracy
  - **Points**: 5
  - **Assignee**: TBD
  - **Dependencies**: TEST-002 (for validation)
  - **Acceptance Criteria**:
    - Reduce false positive rate by 30%
    - Add tile pattern matching for SNES 2bpp/4bpp
    - Implement adaptive stride based on ROM size
  - **Status**: NOT STARTED

- ⬜ **MAP-001**: Enhance code/data classification
  - **Points**: 5
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Improve opcode density calculation (handle M/X flags)
    - Add pointer table detection validation
    - Implement basic control flow analysis
  - **Status**: NOT STARTED

- ⬜ **PERF-001**: Optimize ROM scanning performance
  - **Points**: 3
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Reduce scan time by 50% for 1MB ROMs
    - Add progress indicators
    - Implement multi-threading for block scanning
  - **Status**: NOT STARTED

#### Low Priority
- ⬜ **INT-001**: Create IDA Pro import script
  - **Points**: 3
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Python script that loads rom_map.json
    - Creates bookmarks for each region
    - Sets segment names and types
  - **Status**: NOT STARTED

### Sprint Goals
- Complete HTML visualization
- Improve test coverage to 85%+
- Document all public APIs
- Reduce false positive rate in block detection

### Risks
- **Risk**: Entropy thresholds may need ROM-specific tuning
  - **Mitigation**: Make thresholds configurable via CLI args
- **Risk**: HTML visualization performance on large ROMs
  - **Mitigation**: Implement region consolidation, limit detail level

---

## Sprint 2: Advanced Features (PLANNED)
**Duration**: 2 weeks  
**Goal**: Add advanced analysis and tool integration

### Proposed Stories

#### High Priority
- ⬜ **TILE-001**: Implement tile rendering for graphics validation
  - **Points**: 8
  - **Assignee**: TBD
  - **Dependencies**: VIZ-001
  - **Acceptance Criteria**:
    - Render SNES 2bpp and 4bpp tiles
    - Export as PNG images
    - Display in HTML visualization
  - **Status**: NOT STARTED

- ⬜ **ML-001**: Prototype ML-based block classifier
  - **Points**: 8
  - **Assignee**: TBD
  - **Dependencies**: TEST-002, SCAN-001
  - **Acceptance Criteria**:
    - Train simple classifier on known blocks
    - Achieve >90% accuracy on validation set
    - Document training process
  - **Status**: NOT STARTED

- ⬜ **BATCH-001**: Add multi-ROM batch processing
  - **Points**: 5
  - **Assignee**: TBD
  - **Dependencies**: PERF-001
  - **Acceptance Criteria**:
    - Process directory of ROMs
    - Generate comparative reports
    - Export consolidated results
  - **Status**: NOT STARTED

#### Medium Priority
- ⬜ **EMU-001**: Integration with SNES emulator debugging
  - **Points**: 8
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Export breakpoints for bsnes-plus
    - Generate trace log analysis
    - Map execution coverage back to ROM map
  - **Status**: NOT STARTED

- ⬜ **GUI-001**: Create basic GUI interface
  - **Points**: 13
  - **Assignee**: TBD
  - **Dependencies**: All core features stable
  - **Acceptance Criteria**:
    - Load ROM via file picker
    - Display progress bars
    - Render ROM map visually
    - Export results
  - **Status**: NOT STARTED

#### Low Priority
- ⬜ **MAP-002**: Support ExHiROM and SA-1 mapping
  - **Points**: 5
  - **Assignee**: TBD
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Detect ExHiROM signature
    - Handle SA-1 register mapping
    - Test with known ExHiROM ROMs
  - **Status**: NOT STARTED

---

## Backlog (Unprioritized)

### Features
- **WEB-001**: Web-based interface for ROM analysis
- **EXPORT-001**: Export to radare2 project format
- **AUDIO-001**: Audio extraction and analysis
- **DIFF-001**: ROM comparison and diff tooling
- **CI-001**: Continuous integration with test ROMs

### Technical Debt
- **REFACTOR-001**: Split bob_map.py into smaller modules
- **REFACTOR-002**: Improve error messages and logging
- **REFACTOR-003**: Add type hints to all functions
- **DOC-003**: Create video tutorial walkthrough

### Research
- **RESEARCH-001**: Investigate other SNES compression formats (LZ4, Huffman)
- **RESEARCH-002**: Study automated game logic reconstruction
- **RESEARCH-003**: Compare with existing tools (DiztinGUIsh, etc.)

---

## Definition of Done

A story is considered "Done" when:
- ✅ Code is written and passes all tests
- ✅ Unit tests written with >80% coverage
- ✅ Documentation updated (README, API docs, etc.)
- ✅ Code reviewed (for multi-contributor projects)
- ✅ Integration tested with B.O.B. ROM
- ✅ No critical or high-severity bugs
- ✅ Committed to main branch

---

## Velocity Tracking

| Sprint | Points Planned | Points Completed | Velocity |
|--------|---------------|------------------|----------|
| Sprint 0 | 21 | 21 | 21 (baseline) |
| Sprint 1 | TBD | - | - |
| Sprint 2 | TBD | - | - |

---

## Team Capacity

### Current
- **Contributors**: 1 (solo project)
- **Weekly Hours**: Variable (hobby project)
- **Avg Velocity**: 21 points (baseline from Sprint 0)

### Future
- Open to community contributions
- Looking for: Python developers, SNES RE enthusiasts, testers

---

**Last Updated**: January 27, 2026  
**Next Review**: End of Sprint 1
