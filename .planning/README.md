# Multi-Squad Coordination Guide

**Project:** B.O.B. ROM Analysis Enhancement  
**Branch:** `feature/rom-analysis-enhancement`  
**Sprint Duration:** 20 days  
**Architect:** Lauren

---

## Squad Overview

| Squad | Mission | Tasks | Lead Module |
|-------|---------|-------|-------------|
| **Alpha** 🔵 | Core Analysis Engine | 5 | `bob_lz.py`, `bob_lz_scan.py`, `bob_map.py` |
| **Beta** 🟢 | Graphics & Visualization | 5 | `bob_graphics*.py`, `bob_render.py`, `bob_visualize.py` |
| **Gamma** 🟡 | Level Editor Tools | 5 | `bob_extract*.py`, `bob_inject.py` |
| **Delta** 🟠 | Testing & QA | 5 | `tests/`, `run_full_test_suite.py`, `property_tests.py` |
| **Echo** 🟣 | Documentation & Integration | 5 | `docs/`, `ImportBOBMap.py` |

---

## Directory Structure

```
.planning/
├── README.md                    # This file — coordination guide
├── squad-alpha/                 # Core Analysis Engine
│   ├── mission.md               # Squad objectives & scope
│   ├── task-001.md              # Individual task descriptor
│   ├── task-002.md
│   ├── task-003.md
│   ├── task-004.md
│   ├── task-005.md
│   └── status.md                # Daily progress tracking
├── squad-beta/                  # Graphics & Visualization
│   ├── mission.md
│   ├── task-101.md
│   ├── task-102.md
│   ├── task-103.md
│   ├── task-104.md
│   ├── task-105.md
│   └── status.md
├── squad-gamma/                 # Level Editor Tools
│   ├── mission.md
│   ├── task-201.md
│   ├── task-202.md
│   ├── task-203.md
│   ├── task-204.md
│   ├── task-205.md
│   └── status.md
├── squad-delta/                 # Testing & QA
│   ├── mission.md
│   ├── task-301.md
│   ├── task-302.md
│   ├── task-303.md
│   ├── task-304.md
│   ├── task-305.md
│   └── status.md
└── squad-echo/                  # Documentation & Integration
    ├── mission.md
    ├── task-401.md
    ├── task-402.md
    ├── task-403.md
    ├── task-404.md
    ├── task-405.md
    └── status.md
```

---

## Task Descriptor Format

Each task file follows this template:

```markdown
# Task {ID}: {Title}

**Squad:** {Name}
**Priority:** P0 (Critical) / P1 (High) / P2 (Medium)
**Complexity:** Low / Medium / High
**Estimated Effort:** {hours}
**Status:** ⏳ Pending / 🔄 In Progress / ✅ Complete / ⏸️ Blocked

## Objective
Clear description of what success looks like.

## Context
Background, why this matters, related tasks.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
Implementation hints, relevant files, API references.

## Files to Modify
- `path/to/file.py`

## Dependencies
- **Blocks:** {task IDs}
- **Blocked by:** {task IDs}

## Test Plan
How to verify completion.

## Status Log
- {date}: {update}
```

---

## Coordination Protocol

### Daily Standup (Async)

Each squad updates their `status.md` file:

```markdown
## {Date}

### Completed
- Task {ID}: {title}

### In Progress
- Task {ID}: {title} — {percent}% complete

### Blockers
- {issue description}

### Next
- Planned work for next session
```

### Weekly Sync Checklist

- [ ] Review all squad status files
- [ ] Update QWEN.md commit log
- [ ] Push to origin (feature branch)
- [ ] Re-prioritize blocked tasks
- [ ] Plan next week's focus

### Commit Cadence

| Type | Frequency | Message Format |
|------|-----------|----------------|
| **Task Commit** | Per task | `{squad}: {task-id} — {description}` |
| **Checkpoint** | Daily | `checkpoint: {session summary}` |
| **Milestone** | Per squad complete | `milestone: {squad} mission complete` |

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Task Completion | >80% | Completed / Planned tasks |
| Test Coverage | >90% | `pytest --cov` report |
| Zero Regression | 0 failures | All existing tests pass |
| Documentation | 100% updated | All docs reflect changes |
| Blocked Time | <10% | Time spent blocked / Total time |

---

## Escalation Paths

### Technical Blockers
1. Review related task descriptors
2. Check technical documentation (`docs/`)
3. Consult QWEN.md architecture sections
4. Escalate to Architect

### Dependency Conflicts
1. Check task dependencies in descriptors
2. Coordinate via status.md updates
3. Architect re-prioritizes if needed

### Scope Creep
1. Reference task acceptance criteria
2. Create new task if out of scope
3. Architect approves priority

---

## Quick Reference

### Starting a Task
1. Read task descriptor thoroughly
2. Check dependencies are resolved
3. Update status.md: mark as "In Progress"
4. Begin implementation

### Completing a Task
1. Verify all acceptance criteria met
2. Run relevant tests
3. Update status.md: mark as "Complete"
4. Commit with proper message
5. Update task descriptor status

### Reporting Blockers
1. Update status.md immediately
2. Document the blocker clearly
3. Suggest potential resolutions
4. Wait for Architect guidance

---

## Current Sprint Status

**Sprint:** 1 (Enhancement & Validation)  
**Day:** 1 of 20  
**Tasks Complete:** 0 / 25  
**Squads Active:** 0 / 5

### Squad Status Summary

| Squad | Status | Tasks Done | Next Task |
|-------|--------|------------|-----------|
| Alpha | ⏳ Ready | 0/5 | ALPHA-001 |
| Beta | ⏳ Ready | 0/5 | BETA-001 |
| Gamma | ⏳ Ready | 0/5 | GAMMA-001 |
| Delta | ⏳ Ready | 0/5 | DELTA-001 |
| Echo | ⏳ Ready | 0/5 | ECHO-001 |

---

**Last Updated:** 2026-02-23  
**Next Sync:** End of Day 3 (Phase 1 Review)
