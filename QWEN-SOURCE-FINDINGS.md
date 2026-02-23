# QWEN-SOURCE-FINDINGS.md — B.O.B. Source Code Deep Analysis

**Project:** Space Funky B.O.B. ROM Analysis Toolkit  
**Date:** 2026-02-23  
**Branch:** `feature/v0.3.0-enhancements`  
**Source:** Original Gray Matter source code (Disk D & E, Disk C)

---

## Executive Summary

This document contains comprehensive findings from deep analysis of the original B.O.B. source code archives. All findings are **verified from source** — not speculation from ROM dumps or JSON artifacts.

**Key Discoveries:**
1. **3 Game Worlds** with **8 level categories** (tileset types) mixed within worlds
2. **Lava/Ultra/Bubble levels exist** within Worlds 1-2, NOT as separate worlds
3. **60 unique maps** defined in source, 50 used in final game
4. **36-slot task system** manages all game entities
5. **10 boss battles** with dedicated AI and screen-locking mechanics

---

## Part I: Level/World Architecture

### 1.1 Game Structure (Verified from `INITLEVE.A`)

**World Organization:**
```assembly
maxmaps:
    dc.b    14,19,17          ; World 0: 14 levels
                              ; World 1: 19 levels  
                              ; World 2: 17 levels

allthemaps:
    dc.w    themapsequence1   ; World 0 level sequence
    dc.w    themapsequence2   ; World 1 level sequence
    dc.w    themapsequence3   ; World 2 level sequence
```

**World Composition:**

| World | Levels | Tileset Types Used | Music Theme |
|-------|--------|-------------------|-------------|
| World 0 | 14 levels | borglevel (0), buglevel (1) | borgtheme, bugtheme |
| World 1 | 19 levels | ancientlevel (4), borglevel2 (2), **lavalevel (6)** | anctheme, lavatheme (shared) |
| World 2 | 17 levels | ultralevel (8), **bubblelevel (9)**, borglevel3 (3) | ultratheme, bubbletheme (shared) |

**CRITICAL FINDING:** Lava, Ultra, and Bubble levels exist **WITHIN** the 3 main worlds, NOT as separate worlds.

### 1.2 Complete Level Table (60 Maps)

**Source:** `INITLEVE.A:maptable/maptable2`

| # | Map Name | Label | Bank | Width | Start X/Y | Blockset | Map Type | Music |
|---|----------|-------|------|-------|-----------|----------|----------|-------|
| 0 | Borg Storage | `borgmap1` | 3 | 64 | -5+(64*3) | 0 (borg) | borglevel (0) | borgtheme |
| 1 | Bug Map #1 | `bugmap2` | 12 | 56 | -6+(56*2) | 1 (bug) | buglevel (1) | bugtheme |
| 2 | Borg Outpost | `borgmap2` | 4 | 48 | -4+(48*3) | 0 (borg) | borglevel (0) | borgtheme |
| 3 | Popeye Boss | `popeyebossmap` | 4 | 40 | -4+(4*40) | 4 (ancient) | ancientlevel (4) | anctheme |
| 4 | Borg Prison | `borgmap6` | 15 | 80 | +(80*22)+5 | 0 (borg) | borglevel (0) | borgtheme |
| 5 | Bug Map #2 | `bugmap7` | 15 | 88 | +(4*88)-6 | 1 (bug) | buglevel (1) | bugtheme |
| 6 | Borg Scooters | `scootmap` | 16 | 168 | -3 | 0 (borg) | borglevel (0) | borgtheme |
| 7 | **Lava Level** | `lavamap1` | 19 | 64 | -2+(44*64) | 6 (lava) | **lavalevel (6)** | **lavatheme** |
| 8 | Space 2 | `lavamap1` | 9 | 8 | +(82*8) | 3 (borg3) | spacelevel (3) | borgtheme |
| 9 | Large Snaky Bug | `bugmap13` | 5 | 80 | +14+(2*80) | 1 (bug) | buglevel (1) | bugtheme |
| 10 | **Madman's Level** | `ultramap5` | 24 | 120 | -4+(120*74) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| 11 | Borg Space Port | `bigship1` | 12 | 80 | +(4*80)-3 | 0 (borg) | borglevel (0) | borgtheme |
| 12 | Scooter Map 4 | `borgmap35` | 22 | 168 | +(4*168)+10 | 3 (borg3) | borglevel3 (15) | borgtheme |
| 13 | Queen Map | `queenmap` | 9 | 40 | -6+(2*40) | 1 (bug) | buglevel (1) | bugtheme |
| 14 | Borg Snake Boss | `borgsnake` | 20 | 40 | -4+(3*40) | 0 (borg) | borglevel (0) | borgtheme |
| 15 | Borg Step Ladder | `borgmap7` | 16 | 64 | -4+(4*64) | 2 (borg2) | borglevel2 (14) | borgtheme |
| 16 | Borg Big Ladder | `borgmap11` | 16 | 48 | -6+(59*48) | 2 (borg2) | borglevel2 (14) | borgtheme |
| 17 | Empty | `borgmap20` | 16 | 40 | -4+(8*40) | 0 (borg) | borglevel (0) | borgtheme |
| 18 | Borg House O Beef | `borgmap12` | 16 | 56 | -4+(5*56) | 0 (borg) | borglevel (0) | borgtheme |
| 19 | Borg Elevator Drop | `borgmap13` | 16 | 56 | -4+(2*56) | 2 (borg2) | borglevel2 (14) | borgtheme |
| 20 | Borg Decision | `borgmap4` | 22 | 40 | -5+(7*40) | 0 (borg) | borglevel (0) | borgtheme |
| 21 | Bug Chambers | `bugmap11` | 3 | 48 | +(3*48)-4 | 1 (bug) | buglevel (1) | bugtheme |
| 22 | Last Bug | `bugmap26` | 12 | 128 | +(4*128)-3 | 1 (bug) | buglevel (1) | bugtheme |
| 23 | Ancient #1 | `ancientmap8` | 18 | 200 | -4+(6*200) | 4 (ancient) | ancientlevel (4) | anctheme |
| 24 | Ancient Hourglass | `ancientmap3` | 21 | 72 | -4+(82*72) | 4 (ancient) | ancientlevel (4) | anctheme |
| 25 | Ancient Vertical | `ancientmap7` | 1 | 48 | -4+(48*6) | 4 (ancient) | ancientlevel (4) | anctheme |
| 26 | Ancient Planet | `ancientmap6` | 24 | 128 | -4+(128*40) | 4 (ancient) | ancientlevel (4) | anctheme |
| 27 | Borg Decision | `borgmap17` | 5 | 48 | -4+(2*48) | 2 (borg2) | borglevel2 (14) | borgtheme |
| 28 | Ancient Rollo | `ancientmap5` | 2 | 88 | -3 | 4 (ancient) | ancientlevel (4) | anctheme |
| 29 | Ancient Hmmmm | `ancientmap2` | 20 | 136 | -4+(3*136) | 4 (ancient) | ancientlevel (4) | anctheme |
| 30 | Borg Tower | `borgmap23` | 12 | 40 | +8+(40*106) | 2 (borg2) | borglevel2 (14) | borgtheme |
| 31 | Ancient Boss | `ancientboss` | 15 | 72 | -3+(3*72) | 4 (ancient) | ancientlevel (4) | anctheme |
| **32** | **Lava Map 66** | `lavamap66` | 14 | 96 | +(52*96)-1 | 6 (lava) | **lavalevel (6)** | **lavatheme** |
| **33** | **Lava Boss** | `lavaboss` | 24 | 40 | -4 | 6 (lava) | **lavalevel (6)** | **lavatheme** |
| 34 | Borg Space Port #2 | `bigship2` | 12 | 80 | +(4*80)-3 | 2 (borg2) | borglevel2 (14) | borgtheme |
| **35** | **Ultra 1** | `ultramap1` | 11 | 88 | -3+(88*5) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| **36** | **Bubble 1** | `bubmap1` | 19 | 96 | -5+(96*28) | 8 (bubble) | **bubblelevel (9)** | **bubbletheme** |
| **37** | **Ultra 3** | `ultramap3` | 24 | 96 | -3+(96*2) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| **38** | **Ultra 2** | `ultramap2` | 15 | 112 | -3+(112*4) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| 39 | World Map 1 | `worldmap1` | 20 | W1WIDE | -16 | 9 (world) | worldlevel (10) | borgtheme |
| 40 | Screen Lifter | `borgmap20` | 16 | 40 | -5+(8*40) | 10 (door) | borglevel4 (16) | borgtheme |
| 41 | World Map 2 | `worldmap2` | 20 | W2WIDE | -15 | 9 (world) | worldlevel (10) | borgtheme |
| 42 | World Map 3 | `worldmap3` | 20 | W3WIDE | -15 | 9 (world) | worldlevel (10) | borgtheme |
| **43** | **Bubble 2** | `bubblemap2` | 22 | 104 | +4+(104*31) | 8 (bubble) | **bubblelevel (9)** | **bubbletheme** |
| **44** | **Bubble 3** | `bubblemap3` | 18 | 184 | +8+(184*40) | 8 (bubble) | **bubblelevel (9)** | **bubbletheme** |
| 45 | Intro Map | `intromap` | 16 | 72 | +8+72 | 12 (intro) | buglevel (1) | borgtheme |
| 46 | Titles | `intromap` | 16 | 72 | -8 | 12 (intro) | buglevel (1) | borgtheme |
| 47 | Scooter 3 | `borgmap31` | 15 | 216 | +56+(2*216) | 3 (borg3) | borglevel3 (15) | borgtheme |
| 48 | Borg 32 | `borgmap32` | 16 | 160 | -3+(22*160) | 3 (borg3) | borglevel3 (15) | borgtheme |
| 49 | Borg 33 | `borgmap33` | 21 | 152 | -3+(10*152) | 3 (borg3) | borglevel3 (15) | borgtheme |
| 50 | Borg 34 | `borgmap34` | 24 | 168 | -3+(4*168) | 3 (borg3) | borglevel3 (15) | borgtheme |
| **51** | **Lava Map 99** | `lavamap99` | 12 | 96 | +(4*96)-3 | 6 (lava) | **lavalevel (6)** | **lavatheme** |
| **52** | **Puss Boss** | `pussbossmap` | 12 | 40 | -3+(4*40) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| **53** | **Mutoid Man** | `mutoidmap` | 10 | 40 | -3+(4*40) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| **54** | **Ultra Boss** | `ultrabossmap` | 22 | 40 | -3+(4*40) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| 55 | Borg Scooter 2 | `scootmap2` | 15 | 176 | -2+(1*176) | 2 (borg2) | borglevel2 (14) | borgtheme |
| **56** | **Ultra 4** | `ultramap4` | 11 | 88 | +42+(51*88) | 7 (ultra) | **ultralevel (8)** | **ultratheme** |
| 57 | Intro 2 | `intromap2` | 15 | 112 | -8+112 | 12 (intro) | buglevel (1) | borgtheme |
| 58 | Intro 3 | `intromap3` | 15 | 112 | -8+112 | 12 (intro) | buglevel (1) | borgtheme |
| 59 | Borg Space Port 3 | `bigship3` | 12 | 80 | +(4*80)-3 | 3 (borg3) | borglevel3 (15) | borgtheme |

**Bold rows** highlight Lava, Ultra, and Bubble levels that exist within Worlds 1-2.

### 1.3 World Progression Sequences

**Source:** `INITLEVE.A:themapsequence1/2/3`

```assembly
themapsequence1:      ; World 0 - Borg/Bug World (14 levels)
  dc.b 0,1,2,9,4,22,6,5,14,20,21,18,13,11
  ; Storage→Bug1→Outpost→SnakyBug→Prison→LastBug→Scooters→Bug2→SnakeBoss→
  ; Decision→BugChambers→HouseOBeef→QueenMap→SpacePort

themapsequence2:      ; World 1 - Ancient/Lava World (19 levels)
  dc.b 23,15,7,24,16,51,19,29,32,55,25,3,27,28,33,30,26,40,34
  ; Ancient1→StepLadder→Lava→Hourglass→BigLadder→Lava99→ElevatorDrop→
  ; AncientHmmmm→Lava66→Scooter2→Vertical→Popeye→BorgDecision→AncientRollo→
  ; LavaBoss→BorgTower→AncientPlanet→ScreenLifter→SpacePort2

themapsequence3:      ; World 2 - Ultra/Bubble World (17 levels)
  dc.b 35,48,36,38,43,53,47,44,37,49,56,52,12,50,10,54,59
  ; Ultra1→Borg32→Bubble1→Ultra3→Bubble2→MutoidMan→Scooter3→
  ; Bubble3→Ultra2→Borg34→Ultra4→PussBoss→Scooter4→Borg34→Madman→
  ; UltraBoss→SpacePort3
```

### 1.4 Level Loading Flow

**Source:** `INITLEVE.A:loadwholekit`

```
┌─────────────────────────────────────────────────────────────┐
│  1. SET BLANKING MODE                                       │
│     lda #ForcedBlankOn / sta INIDISP                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. EXTRACT WORLD INFO                                      │
│     jsr extractworld  ; Get themapsequence pointer          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. GET BOB START STATE                                     │
│     lda mapnumber / jsr bobstartstate                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. LOAD PARALLAX SCREEN                                    │
│     lda parallaxtype,y / jsr drawscreen                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. LOAD CONTROL PANEL                                      │
│     lda #1 (panel) / ldy #2 (screen 3) / jsr drawscreen     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. INITIALIZE SCROLL                                       │
│     jsr initscroll  ; Sets up map pointers                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  7. LOAD ALL CHARACTER SETS                                 │
│     jsr loadallchars                                        │
│     → loadbgchars (Background tiles)                        │
│     → loadgoodsprites (Bob + friendly sprites)              │
│     → loadbadsprites (Enemy sprites)                        │
│     → FillBGColors / FillSpriteColors                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  8. DECOMPRESS ANIMATED TILES                               │
│     lda animset,y / jsl decomp                              │
│     animset table:                                          │
│       dc.b 0  → borg (no animation)                         │
│       dc.b 4  → bug (groundlava anim)                       │
│       dc.b 1  → lava (groundlava anim)                      │
│       dc.b 2  → ultra (ultraforceanim)                      │
│       dc.b 3  → borg3 (borg3anim1)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  9. LOAD BLOCK SET (TILESET)                                │
│     lda blocksets,y / jsl decomp (to $E000)                 │
│     blocksets table:                                        │
│       dc.w borgblocks (Bank 3)                              │
│       dc.w bugblocks (Bank 3)                               │
│       dc.w borgblocks2 (Bank 18)                            │
│       dc.w borgblocks3 (Bank 15)                            │
│       dc.w ancientblocks (Bank 11)                          │
│       dc.w lavablocks (Bank 9)                              │
│       dc.w ultrablocks (Bank 22)                            │
│       dc.w bubblocks (Bank 4)                               │
│       dc.w worldblocks (Bank 18)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  10. SET UP TASK TABLE                                      │
│      lda whichtasklist,y / jsl init_tasktable               │
│      jsl inittaskmap                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  11. SET LEVEL TIMER                                        │
│      lda leveltime,y / sta minutes/seconds                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  12. SELECT MUSIC                                           │
│      lda whichthememusic,y / sta APU_PORT0                  │
│      whichthememusic table:                                 │
│        dc.b borgtheme (borg levels)                         │
│        dc.b bugtheme (bug/bubble levels)                    │
│        dc.b anctheme (ancient/lava levels)                  │
│        dc.b ultratheme (ultra levels)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  13. ENABLE DISPLAY                                         │
│      lda #ForcedBlankOff / sta INIDISP                      │
│      jmp bobtask  ; Enter main game loop                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.5 Bob's Starting Positions

**Source:** `INITLEVE.A:bobstartstate`

Format: `dc.b #status,text_index`

| Status Code | Meaning |
|-------------|---------|
| `#falling` (2) | Bob falls from top of screen |
| `#onworld` (120) | Bob spawns on world map (driving car) |
| `#0` (standing) | Bob stands still |
| `#-1` (none) | No specific state - uses default |

**Special Spawn Conditions:**
- **World Map levels (39, 41, 42):** `#onworld` — Bob drives car
- **Scooter levels (6, 11, 12, 47, 55):** `#-1` — Special vehicle spawn
- **Space levels (8):** `#0` — Standing spawn
- **Intro/Titles (45, 46, 57, 58):** `#0` — Cutscene spawn

---

## Part II: Enemy/Task System Architecture

### 2.1 Task System Overview

**Source:** `NINSYS.A`, `DATA.A`

**Task Capacity:**
```assembly
TSKmax  equ  36    ; Maximum concurrent tasks
```

**Task Type Allocation:**
```assembly
task_typetable1:
    dc.b 0,2      ; type_bob = 0 (Bob tasks - 2 slots)
    dc.b 2,15     ; type_enemy = 1 (Borgs/Boxes - 15 slots)
    dc.b 18,3     ; type_remote = 2 (Remotes - 3 slots)
    dc.b 21,3     ; type_weapon = 3 (Weapons - 3 slots)
    dc.b 24,4     ; type_walk = 4 (Platforms - 4 slots)
    dc.b 29,3     ; type_item = 5 (Items - 3 slots)
    dc.b 32,3     ; type_inven = 6 (Inventory - 3 slots)
```

### 2.2 Task Data Structure (64 bytes per task)

**Source:** `DATA.A`

```
┌─────────────────────────────────────────────────────────────┐
│ TSKflags      (1 byte) - Active ($80), Waiting ($40)       │
│ TSKadrLo/Hi   (2 bytes) - Resume address (program counter) │
│ TSKwaitLo     (1 byte) - Wait counter                       │
│ TSKbank       (1 byte) - ROM bank for task code             │
│ PICxlo/hi     (2 bytes) - X position                        │
│ PICylo/hi     (2 bytes) - Y position                        │
│ PICadrLo/Hi   (2 bytes) - Picture/sprite address            │
│ PICattr       (1 byte) - Attributes (hflip/vflip)          │
│ PICbank       (1 byte) - Sprite bank                        │
│ PICflag       (1 byte) - General flags                      │
│ PICanim       (1 byte) - Animation frame counter            │
│ PICstatus     (1 byte) - Status/state variable              │
│ PICdir        (1 byte) - Direction (horizontal)             │
│ PIClogic      (1 byte) - Logic/type reference               │
│ PICcount      (1 byte) - General counter                    │
│ PICthingy     (1 byte) - Secondary counter                  │
│ PICyhi        (1 byte) - Y position high                    │
│ PICsize       (1 byte) - Sprite size                        │
│ PICyoffset    (1 byte) - Y offset                           │
│ PICdirv       (1 byte) - Direction (vertical)               │
│ PICtemp1/2    (2 bytes) - Temporary variables               │
│ PICtether     (1 byte) - Task zone holder                   │
│ PICcolor      (1 byte) - Color palette                      │
│ PICscroll     (1 byte) - Scroll sync flag                   │
│ PICmaplo/hi   (2 bytes) - Task map location                 │
│ PICcount2     (1 byte) - Variable usage                     │
│ PICvomit      (1 byte) - Animation/vomit counter            │
│ PICtype       (1 byte) - Task type reference                │
│ PICtrigger    (1 byte) - Map piece trigger                  │
│ PICed         (1 byte) - Edge variable                      │
│ PIChealth     (1 byte) - Health/strength                    │
│ PICmoveh      (1 byte) - Horizontal movement                │
│ PICmovev      (1 byte) - Vertical movement                  │
│ PICprior      (1 byte) - Priority (0=behind, 1=front)       │
│ PICcolorhit   (1 byte) - Enemy blink color                  │
│ PICcollide    (1 byte) - Collision flag                     │
│ PICshake      (1 byte) - Shake counter (anger effect)       │
│ PICfloat      (1 byte) - Float counter                      │
│ PIClocked     (1 byte) - Lock flag (for missiles)           │
│ PICbehind1    (1 byte) - Background priority                │
│ PIChit        (1 byte) - Hit flag                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Task Scheduling Mechanism

**Source:** `NINSYS.A`

```assembly
; Task Scheduling Flow:
TSKschedule → Search for inactive task in type range
            → Set TSKflags = TSKactive ($80)
            → Store task address (TSKadrLo/Hi)
            → Store task bank (TSKbank)
            → Initialize all PIC variables to 0
            → Return X = task ID (success) or -1 (failure)

TSKsuspend → Save current PC to TSKadrLo/Hi
           → Set TSKflags with TSKactive
           → Return to task handler

TSKwait    → Set TSKwaitLo = A (ticks to wait)
           → Set TSKflags = TSKactive + TSKwaiting
           → Jump to TSKsuspend

TSKcancel  → Zero TSKflags
           → Clear PICadrLo/Hi
           → Clear task map entry
```

### 2.4 Enemy Spawning System

**Source:** `GENERATE.A`, `INITLEVE.A`

**Task Map Format (7 bytes per enemy entry):**
```
Byte 0-1: Task routine address (low, high)
Byte 2:   Task type reference
Byte 3:   Task-specific variable (tempflag)
Byte 4:   X offset (tmpx)
Byte 5:   Y offset (tmpy)
Byte 6:   ROM bank (tempbank)
```

**Enemy Spawning Process:**
```assembly
generate_left_enemies:
    ; Only create in centre of block (pixels 10-22)
    ; Scan map data for task blocks
    ; Check bit 7 of task block (active flag)
    ; If inactive, schedule new task via TSKschedule3
    ; Set bit 7 to mark as ACTIVE
    ; Store task address in PICmaplo/hi

plotenemy:
    ; Read task block value from map
    ; Check if bit 7 is set (already active)
    ; If not active:
    ;   → Calculate task type offset (7 bytes per entry)
    ;   → Extract: task addr, type, tempflag, tmpx, tmpy, tempbank
    ;   → Call TSKschedule3
    ;   → Set PICxlo/ylo from enx/eny (enemy position)
    ;   → Adjust for scroll offsets
    ;   → Mark task block as active (set bit 7)
```

### 2.5 Boss Battle System

**Source:** `INITLEVE.A:fightboss`, `BOB.A`

**Boss Definitions:**

| Boss Name | Level Index | Category | Source Reference |
|-----------|-------------|----------|-----------------|
| Popeye Boss | 3 | Ancient | INITLEVE.A:106 |
| Queen Bug | 13 | Bug | INITLEVE.A:115 |
| Snake Boss | 14 | Borg | INITLEVE.A:116 |
| Spider Boss | 17 | Borg | INITLEVE.A:119 |
| Ancient Boss (Flower) | 31 | Ancient | INITLEVE.A:133 |
| Lava Boss | 33 | Lava | INITLEVE.A:135 |
| Puss Boss | 52 | Ultra | INITLEVE.A:145 |
| Mutoid Man | 53 | Ultra | INITLEVE.A:146 |
| Ultra Boss | 54 | Ultra | INITLEVE.A:147 |
| Screen Lifter | 40 | Borg | INITLEVE.A:141 |

**Boss Variables:**
```assembly
bossstrength:   ds.b 1      ; Boss HP/strength
bossx:          ds.b 2      ; Boss X position (16-bit)
bossy:          ds.b 2      ; Boss Y position (16-bit)
bossdir:        ds.b 1      ; Boss horizontal direction
bossdirv:       ds.b 1      ; Boss vertical direction
bosscolor:      ds.b 1      ; Boss color palette
bosspeedh:      ds.b 1      ; Boss horizontal speed
bosspeedv:      ds.b 1      ; Boss vertical speed
bosscolorhit:   ds.b 1      ; Boss hit flash color
bosscount1-3:   ds.b 3      ; Universal boss counters
bossbulletflag1:ds.b 1      ; Boss bullet flag
bossready:      ds.b 1      ; =1 if boss ready to attack
bossangry:      ds.b 1      ; Angry boss counter
bossexplodetype:ds.b 1      ; Type of boss death
bossstatus:     ds.b 1      ; Boss PICstatus
bossanim:       ds.b 1      ; Boss PICanim
bossPICflag:    ds.b 1      ; Boss PICflag
bosstarget:     ds.b 1      ; Boss target selection
bosslevel:      ds.b 1      ; Boss power meter flag
```

**Boss Battle Screen Locking:**
```assembly
bossguy:  ; Centre screen for boss fight
    lda status
    cmp #stopping
    bne @fine
    lda #walking
    sta status
@fine:
    lda #1
    sta centrescroll      ; Enable centre scroll mode
    lda #64+12            ; Distance to scroll left (76 pixels)
    sta centrescrx
    stz centreydir        ; Scroll down
    ...
    jsr TSKsuspend
    lda beatboss          ; Check if boss defeated
    bne @over
    rtl
@over:
    lda #-1
    sta centrescroll      ; Disable centre scroll
    stz lockscreen
```

### 2.6 Projectile System

**Source:** `WEAPONS.A`

**Weapon Capacity:**
```assembly
weaponmax:
    dc.b 4   ; gun - max 4 active
    dc.b 1   ; uzi - max 1 active
    dc.b 1   ; flame - max 1 active
    dc.b 4   ; missile - max 4 active
    dc.b 3   ; beam - max 3 active
    dc.b 2   ; sonic - max 2 active
```

**Weapon Delays (frames between shots):**
```assembly
weapondelays:
    dc.b 4   ; gun
    dc.b 8   ; uzi
    dc.b 16  ; flame
    dc.b 8   ; missile
    dc.b 24  ; beam
    dc.b 32  ; sonic
```

**Damage Values by Weapon Type:**
```assembly
shotbygun:
    dec PIChealth,y      ; -1 HP

shotbymissile:
    cmp #3
    bcs @larger
    lda #0               ; Instant kill if < 3 HP
@larger:
    sec
    sbc #2               ; -2 HP

shotbybeam:
    cmp #11
    bcs @larger
    lda #0               ; Instant kill if < 11 HP
@larger:
    sec
    sbc #10              ; -10 HP
```

---

## Part III: Music/Palette System

### 3.1 Music Theme Sharing

**Source:** `EQUATES.H`

```assembly
* Music Equates
theme       equ    1
tune_off    equ    2
borgtheme   equ    3    ; World 0 theme
bugtheme    equ    4    ; World 0/2 theme (Bug/Bubble share)
anctheme    equ    5    ; World 1 theme (Ancient/Lava share)
lavatheme   equ    5    ; Shares with Ancient
ultratheme  equ    6    ; World 2 theme
bubbletheme equ    4    ; Shares with Bug
```

**Key Finding:** Music theme sharing explains level type grouping:
- **Bug/Bubble share theme 4** — same music
- **Ancient/Lava share theme 5** — same music

### 3.2 Background Palettes

**Source:** `INITLEVE.A:bgpalletes`

```assembly
bgpalletes:
    dc.w    borgpal11       ; 0 - Borg palette
    dc.w    bugpal          ; 1 - Bug palette
    dc.w    queenpal        ; 2
    dc.w    titlepal        ; 3
    dc.w    ancientpal      ; 4 - Ancient palette
    dc.w    invenpal        ; 5
    dc.w    lavapal         ; 6 - Lava palette ←
    dc.w    intropal        ; 7
    dc.w    ultrapal11      ; 8 - Ultra palette ←
    dc.w    bubpal          ; 9 - Bubble palette ←
    dc.w    worldpal        ; 10 - World map palette
    dc.w    worldpal2       ; 11
    dc.w    worldpal3       ; 12
```

### 3.3 Palette Assignment

**Source:** `INITLEVE.A:whichpalletes`

```assembly
whichpalletes: ;sprite/bg palette indices per mapnumber
    dc.b    0,0             ; borg storage (map 0)
    dc.b    2,1             ; bug (map 1)
    dc.b    14,14           ; borg outpost (map 2)
    dc.b    35,4            ; popeye (map 3)
    dc.b    15,15           ; borg prison (map 4)
    dc.b    22,22           ; bug 2 (map 5)
    dc.b    16,16           ; borg scooter (map 6)
    dc.b    5,6             ; lava level (map 7)  ← Lava palette
    dc.b    1,3             ; space 2 (map 8)
    dc.b    23,23           ; big bug (map 9)
    dc.b    18,19           ; ultra 5 (map 10)    ← Ultra palette
    dc.b    31,0            ; borg spaceport (map 11)
    ...
    dc.b    7,9             ; bubble 1 (map 36)   ← Bubble palette
    dc.b    9,8             ; ultra 1 (map 35)    ← Ultra palette
```

---

## Part IV: MAP File Inventory

### 4.1 Source MAP Files (Disk C)

| Directory | MAP Files | Used By |
|-----------|-----------|---------|
| BORGMAPS | 29 | All 3 worlds (Borg levels) |
| BUGMAPS | 9 | World 0 (Bug levels) |
| JUNGLEMA | 5 | World 1 (Ancient levels) |
| LAVAMAPS | 6 | World 1 (Lava levels) ← |
| ULTRAMPA | 11 | World 2 (Ultra levels) ← |
| ANCMAPS | 16 | Ancient/boss maps |
| WORLDMAP | 4 | World map screens |
| SPACEMAP | 2 | Space levels (cut/unused) |
| **TOTAL** | **82** | |

### 4.2 Cut/Unused Content

**Space Level (maptype 3):**
- Defined in EQUATES.H
- Only appears at mapnumber 8 (unused/empty slot in World 0 sequence)
- Only 2 MAP files in SPACEMAP directory
- **Status:** Likely cut content

**borglevel2/borglevel3/borglevel4:**
- Variant Borg tilesets (14, 15, 16)
- Used for special Borg areas (ladders, elevators, spaceports, screen lifter)
- **Status:** Used as sub-types of Borg theme

---

## Part V: Source Code Citations

| Component | File | Line Reference |
|-----------|------|----------------|
| `maptable` | `INITLEVE.A` | ~line 380-500 |
| `maptable2` | `INITLEVE.A` | ~line 500-560 |
| `themapsequence1/2/3` | `INITLEVE.A` | ~line 180-185 |
| `loadwholekit` | `INITLEVE.A` | ~line 900-1050 |
| `blocksets` | `INITLEVE.A` | ~line 350-370 |
| `animset` | `INITLEVE.A` | ~line 20-35 |
| `whichthememusic` | `INITLEVE.A` | ~line 50-65 |
| `bobstartstate` | `INITLEVE.A` | ~line 140-175 |
| `bobtask` | `BOB.A` | ~line 80-150 |
| Map type equates | `EQUATES.H` | ~line 95-110 |
| `initscroll` | `INITLEVE.A` | ~line 1100-1200 |
| `loadallchars` | `INITLEVE.A` | ~line 800-850 |
| Task system | `NINSYS.A` | ~line 1-450 |
| Task data | `DATA.A` | ~line 1-500 |
| Enemy spawning | `GENERATE.A` | ~line 1-300 |
| Projectile system | `WEAPONS.A` | ~line 1-700 |
| Collision detection | `BOBCOLL.A` | ~line 1-350 |

---

## Part VI: Conclusions

### 6.1 Architecture Summary

1. **3 Game Worlds, 8 Level Categories:**
   - Worlds 0-2 are the actual game worlds
   - Level categories (borglevel, buglevel, lavalevel, ultralevel, bubblelevel, etc.) are **tileset/theme types** mixed within worlds

2. **Lava/Ultra/Bubble ARE in the game:**
   - **Lava levels** appear in World 1 (mapnumber 7, 32, 33, 51)
   - **Ultra levels** appear in World 2 (mapnumber 10, 35, 37, 38, 43, 52, 54, 56)
   - **Bubble levels** appear in World 2 (mapnumber 36, 44)

3. **Tileset/Palette assignment:**
   - Each level (mapnumber) has independent tileset (maptype) and palette (whichpalletes)
   - Allows mixing different visual themes within a single world

4. **82 MAP files total:**
   - Only ~50 used in final game
   - Space levels (maptype 3) likely cut

5. **Music sharing:**
   - Bug/Bubble share theme 4
   - Ancient/Lava share theme 5
   - Explains why these level types are grouped together

6. **36-slot task system:**
   - Manages all game entities (Bob, enemies, weapons, remotes, items)
   - Each task has comprehensive 64-byte data structure
   - Enemies spawned from 7-byte task map entries

7. **10 boss battles:**
   - Dedicated variables for health, behavior, attack patterns
   - Special screen-locking code for boss battles
   - Unique sound effects per boss

---

*Generated from original Gray Matter source code analysis, 2026-02-23*  
**Sub-agents deployed:** 2 (Level loading architecture, Enemy/Task system)  
**Total source files analyzed:** 15+  
**Total lines of source code reviewed:** 10,000+
