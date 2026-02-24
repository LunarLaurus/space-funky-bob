# Level Sequences — Space Funky B.O.B.

**Source:** INITLEVE.A:themapsequence1/2/3 tables  
**Total Maps:** 60 unique maps (50 used in final game)

---

## World 0 (14 levels)

**Sequence:** `0, 1, 2, 9, 4, 22, 6, 5, 14, 20, 21, 18, 13, 11`

| # | Map | Type | Music |
|---|-----|------|-------|
| 1 | 0 | borglevel | borgtheme |
| 2 | 1 | buglevel | bugtheme |
| 3 | 2 | borglevel | borgtheme |
| 4 | 9 | buglevel | bugtheme |
| 5 | 4 | borglevel | borgtheme |
| 6 | 22 | buglevel | bugtheme |
| 7 | 6 | borglevel | borgtheme |
| 8 | 5 | buglevel | bugtheme |
| 9 | 14 | borglevel | borgtheme |
| 10 | 20 | borglevel2 | borgtheme |
| 11 | 21 | buglevel | bugtheme |
| 12 | 18 | borglevel | borgtheme |
| 13 | 13 | buglevel | bugtheme |
| 14 | 11 | borglevel | borgtheme |

---

## World 1 (19 levels)

**Sequence:** `23, 15, 7, 24, 16, 51, 19, 29, 32, 55, 25, 3, 27, 28, 33, 30, 26, 40, 34`

| # | Map | Type | Music |
|---|-----|------|-------|
| 1 | 23 | ancientlevel | anctheme |
| 2 | 15 | borglevel2 | borgtheme |
| 3 | 7 | lavalevel | anctheme |
| 4 | 24 | ancientlevel | anctheme |
| 5 | 16 | borglevel2 | borgtheme |
| 6 | 51 | lavalevel | anctheme |
| 7 | 19 | borglevel2 | borgtheme |
| 8 | 29 | ancientlevel | anctheme |
| 9 | 32 | lavalevel | anctheme |
| 10 | 55 | borglevel2 | borgtheme |
| 11 | 25 | ancientlevel | anctheme |
| 12 | 3 | ancientlevel | anctheme |
| 13 | 27 | borglevel2 | borgtheme |
| 14 | 28 | ancientlevel | anctheme |
| 15 | 33 | lavalevel | anctheme |
| 16 | 30 | borglevel2 | borgtheme |
| 17 | 26 | ancientlevel | anctheme |
| 18 | 40 | borglevel4 | borgtheme |
| 19 | 34 | borglevel2 | borgtheme |

**Note:** Ancient/Lava share music theme 5 (anctheme)

---

## World 2 (17 levels)

**Sequence:** `35, 48, 36, 38, 43, 53, 47, 44, 37, 49, 56, 52, 12, 50, 10, 54, 59`

| # | Map | Type | Music |
|---|-----|------|-------|
| 1 | 35 | ultralevel | ultratheme |
| 2 | 48 | borglevel3 | borgtheme |
| 3 | 36 | bubblelevel | bugtheme |
| 4 | 38 | ultralevel | ultratheme |
| 5 | 43 | ultralevel | ultratheme |
| 6 | 53 | ultralevel | ultratheme |
| 7 | 47 | borglevel3 | borgtheme |
| 8 | 44 | bubblelevel | bugtheme |
| 9 | 37 | ultralevel | ultratheme |
| 10 | 49 | borglevel3 | borgtheme |
| 11 | 56 | ultralevel | ultratheme |
| 12 | 52 | ultralevel | ultratheme |
| 13 | 12 | borglevel3 | borgtheme |
| 14 | 50 | borglevel3 | borgtheme |
| 15 | 10 | ultralevel | ultratheme |
| 16 | 54 | ultralevel | ultratheme |
| 17 | 59 | borglevel3 | borgtheme |

**Note:** Bug/Bubble share music theme 4 (bugtheme)

---

## Level Type Equates (from EQUATES.H)

```assembly
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
borglevel4    equ 16
```

---

## Music Theme Sharing

| Theme | ID | Level Types |
|-------|----|-------------|
| borgtheme | 3 | borg, borg2-4, world, space |
| bugtheme | 4 | bug, **bubble** (shared) |
| anctheme | 5 | ancient, **lava** (shared) |
| ultratheme | 6 | ultra |

---

**Source Citations:**
- Sequences: INITLEVE.A:themapsequence1/2/3
- Level types: EQUATES.H
- Music themes: EQUATES.H:borgtheme/bugtheme/anctheme/ultratheme
