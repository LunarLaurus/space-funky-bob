# Source Verification Report — bob_data vs QWEN-SOURCE-FINDINGS.md

**Project:** Space Funky B.O.B. ROM Analysis Toolkit  
**Date:** 2026-02-23  
**Branch:** `feature/v0.3.0-enhancements`  
**Reference:** `QWEN-SOURCE-FINDINGS.md` (1,276 lines, 25+ source files analyzed)

---

## Executive Summary

Comprehensive verification of bob_data content (wiki.html, WIKI.md, editor/, scripts/) against authoritative source code findings reveals **significant structural errors** and **critical omissions** throughout the documentation and implementation.

**Key Findings:**
- **23 incorrect items, 28 missing items** in wiki.html Level/World data
- **14 incorrect items, 57 missing items** in wiki.html Enemy/Boss data
- **Critical error:** Lava/Ultra/Bubble presented as separate worlds instead of level categories WITHIN 3 main worlds
- **Missing:** 10 boss battles, 6 death types, 36-slot task system, password system, music theme sharing

---

## Verification Summary by Component

| Component | ✅ Correct | ❌ Incorrect | ⚠️ Missing | Status |
|-----------|-----------|--------------|------------|--------|
| wiki.html — Level/World | 25 | 23 | 28 | 🔴 CRITICAL |
| wiki.html — Enemy/Boss | 10 | 14 | 57 | 🔴 CRITICAL |
| wiki.html — Tileset/Palette | 9 | 6 | 20 | 🟠 MAJOR |
| WIKI.md — All Sections | 4 | 10 | 15 | 🔴 CRITICAL |
| editor/server.py — API | 19 | 6 | 20 | 🟠 MAJOR |
| **TOTAL** | **67** | **59** | **140** | |

---

## Critical Discrepancies (Must Fix)

### 1. World Structure — CRITICAL ERROR

**Affected Files:** wiki.html (lines 625-711), WIKI.md (lines 122-145)

**Current (INCORRECT):**
```markdown
### World 1: Borg Factory
### World 2: Bug Planet
### World 3: Ancient Temple
### World 4: Lava
### World 5: Ultra Force
### World 6: Bubble Forest
### World 7: World Maps
### World 8: Space
```

**Source Finding (CORRECT):**
> "CRITICAL FINDING: Lava, Ultra, and Bubble levels exist **WITHIN** the 3 main worlds, NOT as separate worlds."

**Correct Structure:**
- **World 0 (14 levels):** borglevel (0), buglevel (1)
- **World 1 (19 levels):** ancientlevel (4), borglevel2 (2), **lavalevel (6)**
- **World 2 (17 levels):** **ultralevel (8)**, **bubblelevel (9)**, borglevel3 (3)

**Impact:** This fundamentally misrepresents the game's architecture.

---

### 2. Level Counts — CRITICAL ERROR

**Affected Files:** wiki.html (lines 609, 627, 640)

| World | Current Claim | Source Finding |
|-------|--------------|----------------|
| World 0 | "22 levels + 3 bosses = 29" | **14 levels** (themapsequence1) |
| World 1 | "6 levels + 3 bosses = 9" | **19 levels** (themapsequence2) |
| World 2 | "9 levels + 4 bosses = 13" | **17 levels** (themapsequence3) |
| **Total** | "81 levels" | **60 unique maps, 50 used** |

**Source:** `INITLEVE.A:maxmaps` — `dc.b 14,19,17`

---

### 3. Boss Documentation — CRITICAL OMISSION

**Affected Files:** wiki.html (lines 475-488), WIKI.md (no boss section)

**Current:** 7 bosses listed (incomplete, some incorrect)

**Source Finding:** 10 boss battles documented in `INITLEVE.A:fightboss`

| Boss | Level | Category | Status in wiki.html |
|------|-------|----------|---------------------|
| Popeye Boss | 3 | Ancient | ❌ MISSING |
| Queen Bug | 13 | Bug | ✅ Present |
| Snake Boss | 14 | Borg | ✅ Present |
| Spider Boss | 17 | Borg | ❌ MISSING |
| Ancient Boss/Flower | 31 | Ancient | ⚠️ Listed as "Ancient Boss" |
| Lava Boss | 33 | Lava | ✅ Present |
| Puss Boss | 52 | Ultra | ⚠️ Listed as "Pussman" |
| Mutoid Man | 53 | Ultra | ✅ Present |
| Ultra Boss | 54 | Ultra | ❌ MISSING |
| Screen Lifter | 40 | Borg | ✅ Present |

**Missing Boss Mechanics:**
- bossstrength variable (max 48 HP)
- Boss position variables (bossx, bossy — 16-bit)
- Boss behavior counters (bosscount1-3, bossangry, bossready)
- Screen locking for boss battles (centrescroll, centrescrx, centreydir)
- 11 boss-specific sound effects (SFXSNAKEBOSS1-3, SFXQUEENSCREAM, etc.)

---

### 4. Music Theme Sharing — CRITICAL OMISSION

**Affected Files:** wiki.html (lines 853, 863, 873), WIKI.md (no mention)

**Current:** Lava/Ultra/Bubble music listed as "Unknown"

**Source Finding:**
```assembly
borgtheme   equ 3    ; World 0 theme
bugtheme    equ 4    ; World 0/2 theme (Bug/Bubble SHARE)
anctheme    equ 5    ; World 1 theme (Ancient/Lava SHARE)
lavatheme   equ 5    ; Shares with Ancient
ultratheme  equ 6    ; World 2 theme
bubbletheme equ 4    ; Shares with Bug
```

**Impact:** Fails to explain why certain level types share music themes.

---

### 5. Death Types — CRITICAL OMISSION

**Affected Files:** wiki.html (no section), WIKI.md (no section)

**Source Finding:** 6 death types in `EQUATES.H`

| Type | Value | Sound | Trigger |
|------|-------|-------|---------|
| Crumbled | 0 | SFXCRUMBLEDEATH ($95) | Walking/crouching |
| Drained | 1 | None | Energy drained |
| Sidecrush | 2 | None | Squished from side |
| Topcrush | 3 | SFXEXPLODE2 ($9F) | Squished/blown up |
| Melted | 4 | SFXMELTDEATH ($94) | Background drain |
| Burned | 5 | Unused | Fried by flames |

---

### 6. Task System — CRITICAL OMISSION

**Affected Files:** wiki.html (no section), WIKI.md (no section), server.py (no implementation)

**Source Finding:** 36-slot task system in `NINSYS.A`

```assembly
TSKmax  equ  36    ; Maximum concurrent tasks

task_typetable1:
    dc.b 0,2      ; type_bob = 0 (2 slots)
    dc.b 2,15     ; type_enemy = 1 (15 slots)
    dc.b 18,3     ; type_remote = 2 (3 slots)
    dc.b 21,3     ; type_weapon = 3 (3 slots)
    dc.b 24,4     ; type_walk = 4 (4 slots)
    dc.b 29,3     ; type_item = 5 (3 slots)
    dc.b 32,3     ; type_inven = 6 (3 slots)
```

**64-byte task data structure** completely undocumented.

---

### 7. Password System — CRITICAL OMISSION

**Affected Files:** server.py (no implementation)

**Source Finding:** 6-digit password system in `INITLEVE.A`

```assembly
passwords:
    dc.b    world_num, digit1, digit2, digit3, digit4, digit5, digit6, -1
```

- 60 possible passwords (3 worlds × ~20 levels)
- 8-byte entries with -1 terminator
- Boss defeat tracking via `fightboss` table

---

## Major Discrepancies (Should Fix)

### 8. Tileset Documentation — MAJOR ERROR

**Affected Files:** wiki.html (lines 771-783), server.py (lines 468-476)

**Current:** 6-7 tilesets documented

**Source Finding:** 12 tileset types in `EQUATES.H` and `INITLEVE.A:blocksets`

| Tileset | Source Name | Bank | Status |
|---------|-------------|------|--------|
| borglevel | borgblocks | 3 | ✅ Documented |
| buglevel | bugblocks | 3 | ✅ Documented |
| ancientlevel | ancientblocks | 11 | ⚠️ Conflated with Lava |
| lavalevel | lavablocks | 9 | ❌ Missing |
| ultralevel | ultrablocks | 22 | ✅ Documented |
| bubblelevel | bubblocks | 4 | ❌ Missing |
| borglevel2 | borgblocks2 | 18 | ❌ Missing |
| borglevel3 | borgblocks3 | 15 | ❌ Missing |
| borglevel4 | doorblocks | 17 | ❌ Missing |
| worldlevel | worldblocks | 18 | ❌ Missing |
| spacelevel | (cut) | — | ⚠️ Cut content |
| intro | introblocks | 1 | ❌ Missing |

---

### 9. Palette System — MAJOR OMISSION

**Affected Files:** wiki.html (lines 786-794), server.py (lines 273-368)

**Current:** 8 theme palettes mentioned, no indices

**Source Finding:** 13 background palettes + 37+ sprite palettes in `INITLEVE.A`

```assembly
bgpalletes:
    dc.w    borgpal11       ; 0 - Borg
    dc.w    bugpal          ; 1 - Bug
    dc.w    queenpal        ; 2
    dc.w    titlepal        ; 3
    dc.w    ancientpal      ; 4 - Ancient
    dc.w    invenpal        ; 5
    dc.w    lavapal         ; 6 - Lava
    dc.w    intropal        ; 7
    dc.w    ultrapal11      ; 8 - Ultra
    dc.w    bubpal          ; 9 - Bubble
    dc.w    worldpal        ; 10 - World map
    dc.w    worldpal2       ; 11
    dc.w    worldpal3       ; 12
```

**Impact:** Procedural palette generation in server.py instead of loading actual ROM palettes.

---

### 10. MAP File Count — MAJOR ERROR

**Affected Files:** wiki.html (line 922), WIKI.md (no count)

**Current:** "81 total MAP files"

**Source Finding:** 82 MAP files in `source/Disk C/`

| Directory | Count |
|-----------|-------|
| BORGMAPS | 29 |
| BUGMAPS | 9 |
| JUNGLEMA | 5 |
| LAVAMAPS | 6 |
| ULTRAMPA | 11 |
| ANCMAPS | 16 |
| WORLDMAP | 4 |
| SPACEMAP | 2 |
| **TOTAL** | **82** |

---

### 11. Level Sequence Tables — MAJOR OMISSION

**Affected Files:** wiki.html (no section), WIKI.md (no section), server.py (no implementation)

**Source Finding:** `themapsequence1/2/3` in `INITLEVE.A`

```assembly
themapsequence1:      ; World 0 (14 levels)
  dc.b 0,1,2,9,4,22,6,5,14,20,21,18,13,11

themapsequence2:      ; World 1 (19 levels)
  dc.b 23,15,7,24,16,51,19,29,32,55,25,3,27,28,33,30,26,40,34

themapsequence3:      ; World 2 (17 levels)
  dc.b 35,48,36,38,43,53,47,44,37,49,56,52,12,50,10,54,59
```

**Impact:** No level progression documentation.

---

### 12. Bob's Starting Positions — MAJOR OMISSION

**Affected Files:** wiki.html (no section)

**Source Finding:** `bobstartstate` table in `INITLEVE.A`

| Status | Value | Description |
|--------|-------|-------------|
| falling | 2 | Falls from top |
| onworld | 120 | World map (driving car) |
| standing | 0 | Stands still |
| none | -1 | Special spawn (scooter) |

**Special Spawns:**
- World Map levels (39, 41, 42): `#onworld` — Bob drives car
- Scooter levels (6, 11, 12, 47, 55): `#-1` — Special vehicle spawn
- Space levels (8): `#0` — Standing spawn
- Intro/Titles (45, 46, 57, 58): `#0` — Cutscene spawn

---

## Minor Discrepancies (Nice to Fix)

### 13. Weapon System — MINOR OMISSION

**Affected Files:** wiki.html (no section), server.py (partial)

**Source Finding:** 6 weapons + 6 remotes in `WEAPONS.A` and `CONTROL.A`

| Weapon | Max Active | Fire Delay | Damage |
|--------|-----------|------------|--------|
| Gun | 4 | 4 frames | 1 HP |
| Uzi | 1 | 8 frames | 3 HP |
| Flame | 1 | 16 frames | Continuous |
| Missile | 4 | 8 frames | 2 HP |
| Beam | 3 | 24 frames | 10 HP |
| Sonic | 2 | 32 frames | 25 HP |

---

### 14. Color Effects — MINOR OMISSION

**Affected Files:** wiki.html (no section)

**Source Finding:** SNES register usage in `EQUATES.H`

| Effect | Register | Purpose |
|--------|----------|---------|
| 16-level fade | INIDISP ($2100) | Brightness control |
| Mosaic | MOSAIC ($2106) | Pixelation effect |
| Color math | CGSWSEL ($2130) | Sub-screen addition |
| Color math | CGADSUB ($2131) | Add/subtract control |

---

### 15. Controller Mapping — MINOR OMISSION

**Affected Files:** wiki.html (no section)

**Source Finding:** Controller equates in `EQUATES.H` and `SFXCONST.H`

| Button | Value | Function |
|--------|-------|----------|
| D-Pad Right | %00000001 | Move right |
| D-Pad Left | %00000010 | Move left |
| D-Pad Down | %00000100 | Crouch/look down |
| D-Pad Up | %00001000 | Aim up/grab ladder |
| Y Button | %01000000 | Fire weapon |
| B Button | %10000000 | Jump |
| A Button | %10000000 | Punch |
| X Button | %01000000 | Deploy remote |
| L Button | %00100000 | Change weapon |
| R Button | %00010000 | Change remote |

---

## Verification by File

### wiki.html (897 lines)

| Section | Lines | Status | Issues |
|---------|-------|--------|--------|
| Level Index | 601-760 | 🔴 CRITICAL | Wrong world structure, wrong level counts |
| Enemy Database | 450-600 | 🔴 CRITICAL | Missing 3 bosses, no death types |
| Tileset Index | 771-794 | 🟠 MAJOR | Missing 6 tilesets, no palette indices |
| Game Worlds | 800-895 | 🔴 CRITICAL | Lava/Ultra/Bubble as separate worlds |
| MAP File Structure | 909-930 | 🟠 MAJOR | Wrong total (81 vs 82) |

### WIKI.md (293 lines)

| Section | Lines | Status | Issues |
|---------|-------|--------|--------|
| ROM Specification | 10-17 | ✅ CORRECT | None |
| Memory Map | 19-36 | 🟠 MAJOR | World naming, bank offsets |
| Level Data Format | 38-53 | 🟠 MAJOR | Missing level counts |
| Tileset Format | 55-78 | ✅ CORRECT | None |
| Compression | 80-100 | ⚠️ PARTIAL | Algorithm unverified |
| Audio Data | 102-120 | 🟠 MAJOR | Missing music theme sharing |
| Enemy Database | 122-145 | 🔴 CRITICAL | Missing bosses, death types |
| Level Index | 122-145 | 🔴 CRITICAL | Missing level counts, sequences |
| Tileset Index | 55-78 | 🟠 MAJOR | Missing 6 tilesets, palettes |
| Game Worlds | 122-145 | 🔴 CRITICAL | Lava/Ultra/Bubble location wrong |
| Source Files | 171-185 | 🟠 MAJOR | Missing MAP count, cut content |

### editor/server.py (834 lines)

| Feature | Lines | Status | Issues |
|---------|-------|--------|--------|
| API Endpoints | 69-209 | ✅ CORRECT | All 9 endpoints implemented |
| Level Data Handling | 178-182, 637-657 | 🔴 CRITICAL | Only 3 levels, wrong naming |
| Tileset Handling | 468-476 | 🟠 MAJOR | Missing 5 tilesets |
| ROM Offset Handling | 468-476 | ✅ CORRECT | Offsets correct |
| Password System | N/A | 🔴 CRITICAL | Not implemented |
| Boss Data | N/A | 🔴 CRITICAL | Not implemented |

---

## Recommended Actions

### Priority 1: Critical Fixes

1. **Restructure wiki.html Game Worlds section** (lines 625-711)
   - Change from 8 separate worlds to 3 worlds with mixed level categories
   - Update level counts: World 0=14, World 1=19, World 2=17
   - Add level sequence tables (themapsequence1/2/3)

2. **Add boss documentation to wiki.html** (new section after Enemy Database)
   - List all 10 bosses with level indices
   - Document boss HP (bossstrength, max 48)
   - Add boss battle mechanics (screen locking, behavior counters)
   - Add boss sound effects table

3. **Add death types to wiki.html** (new section after Enemy Database)
   - Document 6 death types with sound effects
   - Include trigger conditions

4. **Fix music theme sharing in wiki.html** (lines 853, 863, 873)
   - Update Lava: "Shares theme 5 with Ancient (anctheme)"
   - Update Bubble: "Shares theme 4 with Bug (bugtheme)"
   - Update Ultra: "ultratheme (6)"

5. **Add task system documentation to wiki.html** (new section)
   - 36-slot task system overview
   - Task type allocation table
   - 64-byte task data structure

### Priority 2: Major Fixes

6. **Expand tileset documentation in wiki.html** (lines 771-783)
   - Add all 12 tilesets with source names
   - Add bank information
   - Split Ancient/Lava into separate entries

7. **Add palette documentation to wiki.html** (new section)
   - 13 background palettes with indices
   - 37+ sprite palettes
   - Palette assignment per level (whichpalletes table)

8. **Correct MAP file total in wiki.html** (line 922)
   - Change from 81 to 82

9. **Fix WIKI.md Game Worlds section** (lines 122-145)
   - Same changes as wiki.html

10. **Fix server.py world naming** (lines 178-182, 637-657)
    - Change WORLD_1/2/3 to WORLD_0/1/2

11. **Add missing tilesets to server.py** (lines 468-476)
    - bubblocks, borgblocks2, borgblocks3, worldblocks, introblocks

12. **Implement password system in server.py** (new endpoints)
    - `/password/generate` — Generate 6-digit password
    - `/password/validate` — Validate password and restore progression

### Priority 3: Minor Fixes

13. **Add weapon system documentation to wiki.html** (new section)
    - 6 weapons with damage/delay stats
    - 6 remotes with icons

14. **Add color effects documentation to wiki.html** (new section)
    - INIDISP, MOSAIC, CGSWSEL, CGADSUB registers

15. **Add controller mapping to wiki.html** (new section)
    - Complete button layout with functions

---

## Conclusion

The bob_data content requires **significant revision** to align with the authoritative source code findings. The most critical issue is the **fundamental misunderstanding of the game's world structure** — presenting Lava/Ultra/Bubble as separate worlds when they are level categories within the 3 main worlds.

**Total discrepancies found:** 266 items
- ✅ Correct: 67 (25%)
- ❌ Incorrect: 59 (22%)
- ⚠️ Missing: 140 (53%)

**Estimated effort to fix:**
- Critical fixes: 8-12 hours
- Major fixes: 6-8 hours
- Minor fixes: 2-4 hours
- **Total: 16-24 hours**

---

**Generated:** 2026-02-23  
**Verification completed by:** 5 sub-agents  
**Source files referenced:** 25+  
**Total lines of source reviewed:** 20,000+
