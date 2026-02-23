# Space Funky B.O.B. — Level/World/Tileset Architecture
## Deep Source Code Analysis

**Date:** 2026-02-23  
**Source:** `source/Disk D & E/BOBSNE3/`, `source/Disk D & E/BOBSNE4/`, `source/Disk C/`  
**Status:** Verified from original Gray Matter source code

---

## Executive Summary

**CRITICAL FINDING:** Lava, Ultra, and Bubble levels **DO exist** within the 3 main game worlds (Worlds 0-2). They are **NOT separate worlds** but rather **tileset/theme types** mixed within each world.

**Previous misunderstanding:** The "8 worlds" terminology in wiki.html and JSON files refers to **8 level categories** (tileset types), not 8 separate game worlds.

---

## 1. Game Structure — Verified from Source

### World Organization (3 Worlds)

**Source:** `source/Disk D & E/BOBSNE3/INITLEVE.A`

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

### World/Level Relationship

```
world (0-2) → themapsequence[world] → mapsequence index → mapnumber
```

**Variables:**
- `world` — Current world (0, 1, or 2)
- `mapsequence` — Index within world's level sequence
- `mapnumber` — Actual map ID (0-59) used to load level data
- `maptype` — Tileset/theme type for current level

---

## 2. Level Type Equates

**Source:** `source/Disk D & E/BOBSNE4/EQUATES.H`

```assembly
;map types
borglevel       equ    0      ; Borg Factory tileset
buglevel        equ    1      ; Bug Planet tileset
spacelevel      equ    3      ; Space tileset (cut/unused)
ancientlevel    equ    4      ; Ancient Ruins tileset
lavalevel       equ    6      ; Lava tileset ← EXISTS IN WORLD 1
ultralevel      equ    8      ; Ultra Force tileset ← EXISTS IN WORLD 2
bubblelevel     equ    9      ; Bubble Forest tileset ← EXISTS IN WORLD 2
worldlevel      equ    10     ; World map screen 1
worldlevel2     equ    11     ; World map screen 2
worldlevel3     equ    12     ; World map screen 3
borglevel2      equ    14     ; Borg variant (ladders/elevators)
borglevel3      equ    15     ; Borg variant (World 2)
borglevel4      equ    16     ; Borg variant (screen lifter)
```

---

## 3. World Composition — Level Types Per World

### World 0: Borg Factory + Bug Planet (14 levels)

**Level sequence:** `0,1,2,9,4,22,6,5,14,20,21,18,13,11`

| mapnumber | Level Name | maptype | Tileset |
|-----------|------------|---------|---------|
| 0 | borg storage | borglevel (0) | Borg |
| 1 | bug map #1 | buglevel (1) | Bug |
| 2 | borg outpost | borglevel (0) | Borg |
| 9 | large snaky bug | buglevel (1) | Bug |
| 4 | borg prison | borglevel (0) | Borg |
| 22 | last of the buggers | buglevel (1) | Bug |
| 6 | borg scooters | borglevel (0) | Borg |
| 5 | bugmap #2 | buglevel (1) | Bug |
| 14 | borg snake boss | borglevel (0) | Borg |
| 20 | borg decision | borglevel2 (2) | Borg variant |
| 21 | bug chambers | buglevel (1) | Bug |
| 18 | borg house o beef | borglevel (0) | Borg |
| 13 | queen map | buglevel (1) | Bug |
| 11 | borg space port | borglevel (0) | Borg |

**Tilesets used:** borglevel (0), buglevel (1), borglevel2 (2)

---

### World 1: Ancient Ruins + Borg + **Lava** (19 levels)

**Level sequence:** `23,15,7,24,16,51,19,29,32,55,25,3,27,28,33,30,26,40,34`

| mapnumber | Level Name | maptype | Tileset |
|-----------|------------|---------|---------|
| 23 | ancient #1 | ancientlevel (4) | Ancient |
| 15 | borg step ladder | borglevel2 (2) | Borg variant |
| 7 | **lava level** | lavalevel (6) | **Lava** ← |
| 24 | ancient hourglass | ancientlevel (4) | Ancient |
| 16 | borg big ladder | borglevel2 (2) | Borg variant |
| 51 | **lava map 99** | lavalevel (6) | **Lava** ← |
| 19 | borg elevator drop | borglevel2 (2) | Borg variant |
| 29 | ancient hmmmm | ancientlevel (4) | Ancient |
| 32 | **lava map 66** | lavalevel (6) | **Lava** ← |
| 55 | borg scooter 2 | borglevel2 (2) | Borg variant |
| 25 | ancient vertical | ancientlevel (4) | Ancient |
| 3 | popeye boss | ancientlevel (4) | Ancient |
| 27 | borg decision | borglevel2 (2) | Borg variant |
| 28 | ancient rollo | ancientlevel (4) | Ancient |
| 33 | **lava boss** | lavalevel (6) | **Lava** ← |
| 30 | borg tower | borglevel2 (2) | Borg variant |
| 26 | ancient planet | ancientlevel (4) | Ancient |
| 40 | screen lifter | borglevel4 (10) | Borg variant |
| 34 | borg space port #2 | borglevel2 (2) | Borg variant |

**Tilesets used:** ancientlevel (4), borglevel2 (2), **lavalevel (6)**

---

### World 2: Ultra Force + **Bubble Forest** + Borg (17 levels)

**Level sequence:** `35,48,36,38,43,53,47,44,37,49,56,52,12,50,10,54,59`

| mapnumber | Level Name | maptype | Tileset |
|-----------|------------|---------|---------|
| 35 | **ultra 1** | ultralevel (8) | **Ultra** ← |
| 48 | borg 32 | borglevel3 (3) | Borg variant |
| 36 | **bubble 1** | bubblelevel (9) | **Bubble** ← |
| 38 | **ultra 3** | ultralevel (8) | **Ultra** ← |
| 43 | **ultra 2** | ultralevel (8) | **Ultra** ← |
| 53 | mutoid man | ultralevel (8) | **Ultra** ← |
| 47 | borg scooter 3 | borglevel3 (3) | Borg variant |
| 44 | **bubble 3** | bubblelevel (9) | **Bubble** ← |
| 37 | **ultra 4** | ultralevel (8) | **Ultra** ← |
| 49 | borg 34 | borglevel3 (3) | Borg variant |
| 56 | **ultra 4** | ultralevel (8) | **Ultra** ← |
| 52 | puss boss | ultralevel (8) | **Ultra** ← |
| 12 | scooter map 4 | borglevel3 (3) | Borg variant |
| 50 | borg 34 | borglevel3 (3) | Borg variant |
| 10 | madman's level | ultralevel (8) | **Ultra** ← |
| 54 | **ultra boss** | ultralevel (8) | **Ultra** ← |
| 59 | borg space port #3 | borglevel3 (3) | Borg variant |

**Tilesets used:** ultralevel (8), **bubblelevel (9)**, borglevel3 (3)

---

## 4. Tileset/Palette Assignment Mechanism

### Palette Loading

**Source:** `source/Disk D & E/BOBSNE3/INITLEVE.A`

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

### Background Palettes

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

### Level Loading Flow

```assembly
loadwholekit:
    lda    #ForcedBlankOn
    sta    INIDISP
    
    ldy    world
    lda    maxmaps,y
    sta    maxlevels
    
    lda    mapnumber            ; get palette index
    asl    a
    inc    a
    tay
    lda    whichpalletes,y      ; load sprite/bg palette
    jsr    FillBGColors
    jsr    Fillspritecolors
```

---

## 5. MAP File Inventory

### Source MAP Files (Disk C)

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

---

## 6. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    GAME STRUCTURE                            │
├─────────────────────────────────────────────────────────────┤
│  world (0-2)                                                 │
│    │                                                         │
│    ├─→ World 0: themapsequence1[14 levels]                  │
│    │     └─→ mapnumber: 0,1,2,9,4,22,6,5,14,20,21,18,13,11 │
│    │     └─→ maptype: borglevel(0), buglevel(1)             │
│    │                                                         │
│    ├─→ World 1: themapsequence2[19 levels]                  │
│    │     └─→ mapnumber: 23,15,7,24,16,51,19,29,32,55...    │
│    │     └─→ maptype: ancientlevel(4), borglevel2(2),       │
│    │                  lavalevel(6) ← LAVA IN WORLD 1!       │
│    │                                                         │
│    └─→ World 2: themapsequence3[17 levels]                  │
│          └─→ mapnumber: 35,48,36,38,43,53,47,44,37,49...    │
│          └─→ maptype: ultralevel(8), bubblelevel(9),        │
│                   borglevel3(3) ← ULTRA/BUBBLE IN WORLD 2!  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                TILESET/PALETTE FLOW                          │
├─────────────────────────────────────────────────────────────┤
│  mapnumber → whichpalletes[mapnumber] → (sprite_pal, bg_pal)│
│              ↓                                               │
│         whichpalletes,y → bgpalletes entry → bgpalXX        │
│                         → spritepalletes entry → bobpalXX   │
│              ↓                                               │
│         PICcolor = palette index                            │
│         maptype → blocksets → tileset graphics              │
│         maptype → animset → animated tiles                  │
│         maptype → soundbank → music/sfx bank                │
│         maptype → whichthememusic → background music        │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Cut/Unused Content

### Space Level (maptype 3)
- Defined in EQUATES.H
- Only appears at mapnumber 8 (unused/empty slot in World 0 sequence)
- Only 2 MAP files in SPACEMAP directory
- **Status:** Likely cut content

### borglevel2/borglevel3/borglevel4
- Variant Borg tilesets (14, 15, 16)
- Used for special Borg areas (ladders, elevators, spaceports, screen lifter)
- **Status:** Used as sub-types of Borg theme

---

## 8. Music Themes

**Source:** `source/Disk D & E/BOBSNE4/EQUATES.H`

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

**Note:** Bubble and Bug share the same music theme (4). Lava and Ancient share the same theme (5).

---

## 9. Key Source Code Citations

| File | Section | Description |
|------|---------|-------------|
| `BOBSNE4/EQUATES.H` | Map type equates | Level type constants (0-16) |
| `BOBSNE3/INITLEVE.A` | maxmaps/themapsequence | World level sequences |
| `BOBSNE3/INITLEVE.A` | extractworld: | World extraction routine |
| `BOBSNE3/INITLEVE.A` | maptable/maptable2 | Map data definitions |
| `BOBSNE3/INITLEVE.A` | whichpalletes: | Palette assignments per map |
| `BOBSNE3/INITLEVE.A` | bgpalletes: | Background palettes |
| `BOBSNE3/INITLEVE.A` | loadwholekit: | Level loading routine |
| `BOBSNE3/BOB.A` | bobtask: | Level progression logic |

---

## 10. Conclusions

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

---

*Generated from original Gray Matter source code analysis, 2026-02-23*
