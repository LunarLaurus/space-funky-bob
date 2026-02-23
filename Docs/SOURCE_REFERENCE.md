# B.O.B. Source Reference Document

**Authoritative Reference for Level and ROM Data**

*Last Updated: 2026-02-23*

---

## Overview

This document serves as the **single source of truth** for B.O.B. (Space Funky B.O.B.) game data, derived directly from the original source code files. All information herein is extracted from the official SNES development sources.

**Primary Sources:**
- `source/Disk C/**/*.MAP` - Level map files (81 unique MAP files)
- `source/Disk D & E/BOBSNE4/EQUATES.H` - Game equates and constants
- `source/Disk D & E/BOBSNE3/BORG.A` - Enemy logic and definitions
- `source/Disk D & E/BOBSNE1/*.ASP` - Enemy sprite definitions

---

## 1. Level Categories (from EQUATES.H)

The following level type equates are defined in `source/Disk D & E/BOBSNE4/EQUATES.H`:

```assembly
;map types

borglevel     equ 0
buglevel      equ 1
spacelevel    equ 3
ancientlevel  equ 4
lavalevel     equ 6
ultralevel    equ 8
bubblelevel   equ 9
worldlevel    equ 10
worldlevel2   equ 11
worldlevel3   equ 12
borglevel2    equ 14
borglevel3    equ 15
borglevel4    equ 16    ;door!!!
```

---

## 2. MAP File Inventory

Complete inventory of MAP files from `source/Disk C/`:

| Directory   | MAP Files | Description                          |
|-------------|-----------|--------------------------------------|
| BORGMAPS    | 29        | Borg Factory levels + bosses         |
| BUGMAPS     | 9         | Bug Planet levels + bosses           |
| ANCMAPS     | 16        | Ancient Ruins levels + bosses        |
| LAVAMAPS    | 6         | Lava world levels + boss             |
| JUNGLEMA    | 5         | Bubble Forest levels                 |
| ULTRAMPA    | 11        | Ultra Force levels + bosses          |
| WORLDMAP    | 4         | World map screens                    |
| SPACEMAP    | 2         | Space levels                         |
| **TOTAL**   | **82**    | **Unique MAP files**                 |

### 2.1 Detailed File Listing

#### BORGMAPS (29 files)
```
BIGSHIP1.MAP, BIGSHIP2.MAP, BIGSHIP3.MAP, BORG017.MAP, BORG1.MAP,
BORG10.MAP, BORG11.MAP, BORG12.MAP, BORG13.MAP, BORG17.MAP,
BORG2.MAP, BORG20.MAP, BORG23.MAP, BORG3.MAP, BORG31.MAP,
BORG32.MAP, BORG33.MAP, BORG34.MAP, BORG35.MAP, BORG39.MAP,
BORG4.MAP, BORG6.MAP, BORG7.MAP, BORG8.MAP, BORG88.MAP,
BORG89.MAP, FLOWER.MAP, SNAKBOSS.MAP, TANKBOSS.MAP
```

#### BUGMAPS (9 files)
```
BUG1.MAP, BUG11.MAP, BUG13.MAP, BUG2.MAP, BUG26.MAP,
BUG7.MAP, BUGQUEEN.MAP, QUEEN.MAP, QUEEN2.MAP
```

#### ANCMAPS (16 files)
```
A1.MAP, ANC002.MAP, ANC1.MAP, ANC2.MAP, ANC3.MAP, ANC4.MAP,
ANC5.MAP, ANC6.MAP, ANC7.MAP, ANC8.MAP, ANC8A.MAP,
ANCBOSS.MAP, PODBOSS.MAP, POPBOSS.MAP, PUSSBOSS.MAP, TEMP001.MAP
```

#### LAVAMAPS (6 files)
```
LAVA1.MAP, LAVA1A.MAP, LAVA1TES.MAP, LAVA66.MAP, LAVA99.MAP, LAVABOSS.MAP
```

#### JUNGLEMA (5 files)
```
BUB1.MAP, BUBBLE1.MAP, BUBBLE2.MAP, BUBBLE3.MAP, BUBPARA.MAP
```

#### ULTRAMPA (11 files)
```
MUTOID.MAP, PUSSBOSS.MAP, ULTRA1.MAP, ULTRA1A.MAP, ULTRA1B.MAP,
ULTRA2.MAP, ULTRA3.MAP, ULTRA4.MAP, ULTRA5.MAP, ULTRBOSS.MAP, ULTRTES.MAP
```

#### WORLDMAP (4 files)
```
WOR1.MAP, WOR1P.MAP, WOR2.MAP, WOR3.MAP
```

#### SPACEMAP (2 files)
```
SPAC1.MAP, SPAC2.MAP
```

---

## 3. ROM Offsets

Confirmed and TBD ROM offsets for world data:

| World                  | ROM Offset | SNES Address | Status        |
|------------------------|------------|--------------|---------------|
| World 1 (Borg)         | 0xD4000    | 0x9AC000     | Confirmed     |
| World 2 (Bug)          | 0xE4000    | 0x9CC000     | Confirmed     |
| World 3 (Ancient)      | 0xF4000    | 0x9EC000     | Confirmed     |
| World 4 (Lava)         | TBD        | TBD          | Unknown       |
| World 5 (Ultra)        | TBD        | TBD          | Unknown       |
| World 6 (Bubble)       | TBD        | TBD          | Unknown       |
| World 7 (Maps)         | N/A        | N/A          | UI screens    |
| World 8 (Space)        | TBD        | TBD          | Unknown       |

---

## 4. Enemy Definitions

Enemy IDs and definitions from `source/Disk D & E/BOBSNE3/BORG.A` and `source/Disk D & E/BOBSNE1/*.ASP`:

### 4.1 Verified Enemy IDs

| ID  | Enemy Name        | Source File | Description                    |
|-----|-------------------|-------------|--------------------------------|
| 38  | backarm_emerge    | BORG.A:37   | Arm boss arm emerges           |
| 101 | bubbleman_walk    | BORG.A      | Bubble man walking             |

### 4.2 Enemy Sprite Files

The following enemy sprite definition files exist in `source/Disk D & E/BOBSNE1/`:

- **FLOWER.ASP** - Flower boss sprite data (verified exists)
- **BORG*.ASP** - Borg enemy sprites
- **BUG*.ASP** - Bug enemy sprites
- **ANC*.ASP** - Ancient enemy sprites
- **BUB*.ASP** - Bubble Forest enemy sprites
- **ULTRA*.ASP** - Ultra Force enemy sprites

### 4.3 Enemy Type Equates (excerpt from BORG.A)

```assembly
; borg types - used by PIClogic
borg_guard      equ 1       ;same as patrol now
borg_patrol     equ 2
borg_shooter    equ 3
borg_jumper     equ 4
borg_small      equ 5
borg_flyer      equ 6
borg_ducker     equ 7
borg_flyerv     equ 8       ;vertical flyer
borg_tosser     equ 9

; borg actions - used by PICstatus
borg_shoot      equ 1
borg_start      equ 2
borg_stop       equ 3
borg_prejump    equ 4
borg_land       equ 5
borg_jump       equ 6
borg_duck       equ 7
borg_getup      equ 0
borg_turn       equ 8
borg_minitank   equ 9
hiddengun_rise  equ 10
flygun_shoot    equ 11
zapperbeam      equ 12      ;hovering zapper beam
queensplat      equ 13      ;queen splatting apart
queen_hole      equ 14      ;queen leggies wiggling about
snakehead       equ 15      ;borg boss snakehead
borg_stand      equ 16
borg_move       equ 17
falling_brick   equ 18      ;falling ancient brick
flower          equ 19      ;open arm boss rose flower thingy

; Enemy action IDs (partial list)
cockroach       equ 29
egg             equ 30
worker_walk     equ 31
worker_jump     equ 32
worker_land     equ 33
worker_fire     equ 34
venomball       equ 35
worker_stand    equ 36
dropper_left    equ 37
backarm_emerge  equ 38      ;arm boss arm emerges
dropper_chew    equ 39

; ... (additional enemy definitions continue)

bubbleman_walk  equ 101     ;bubble man walking
bubbleman_stand equ 102     ;bubble man standing and jiggling
```

---

## 5. Important Notes

### 5.1 Data Source Warning

> **WARNING:** JSON files located in `data/extracted/` are **working artifacts** generated from ROM analysis scripts. They are **NOT authoritative sources**.
>
> **Always verify data against the original source code** in the `source/` directory before making production decisions.

### 5.2 Source File Locations

| Data Type          | Primary Source Location                    |
|--------------------|-------------------------------------------|
| Level Maps         | `source/Disk C/**/*.MAP`                  |
| Game Equates       | `source/Disk D & E/BOBSNE4/EQUATES.H`     |
| Enemy Logic        | `source/Disk D & E/BOBSNE3/*.A`           |
| Enemy Sprites      | `source/Disk D & E/BOBSNE1/*.ASP`         |
| Boss Definitions   | `source/Disk D & E/BOBSNE3/BORG.A`        |

### 5.3 File Count Discrepancy Note

The MAP file count shows 82 files in the source directory. Some documentation may reference 81 files - this discrepancy may be due to:
- Duplicate files across directories (e.g., PUSSBOSS.MAP appears in both ANCMAPS and ULTRAMPA)
- Test/temporary files (e.g., TEMP001.MAP, LAVA1TES.MAP, ULTRTES.MAP)
- Files added during development but not used in final ROM

---

## 6. Revision History

| Date       | Version | Changes                              |
|------------|---------|--------------------------------------|
| 2026-02-23 | 1.0     | Initial document creation            |

---

*This document is maintained as part of the Space Funky B.O.B. preservation project.*
