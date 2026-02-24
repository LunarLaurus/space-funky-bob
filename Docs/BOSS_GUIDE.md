# Boss Battle Guide — Space Funky B.O.B.

**Source:** INITLEVE.A:fightboss table, BOB.A boss mechanics  
**Total Bosses:** 10

---

## Boss Overview

All bosses have **48 HP** (bossstrength variable max).

| # | Boss | Level | Category | Sounds |
|---|------|-------|----------|--------|
| 1 | Popeye Boss | 3 | Ancient | SFXANCIENTBOSS |
| 2 | Queen Bug | 13 | Bug | SFXQUEENSCREAM |
| 3 | Snake Boss | 14 | Borg | SFXSNAKEBOSS1-3 |
| 4 | Spider Boss | 17 | Borg | SFXSPIDERBOSS |
| 5 | Ancient Boss | 31 | Ancient | SFXFLOWERBOSS |
| 6 | Lava Boss | 33 | Lava | SFXLAVABOSS |
| 7 | Screen Lifter | 40 | Borg | SFXLIFTER |
| 8 | Puss Boss | 52 | Ultra | SFXPUSSMANBELCH |
| 9 | Mutoid Man | 53 | Ultra | SFXMUTOID |
| 10 | Ultra Boss | 54 | Ultra | SFXULTRABOSS |

---

## Boss Mechanics

### Variables (from BOB.A)
- **bossstrength:** HP (max 48)
- **bossx, bossy:** 16-bit positions
- **bossdir, bossdirv:** Direction (horizontal/vertical)
- **bosspeedh, bosspeedv:** Speed
- **bosscount1-3:** Behavior counters
- **bossangry:** Aggression state
- **bossready:** Attack ready flag

### Screen Locking
During boss battles:
- `centrescroll` = 1 (enable centre scroll mode)
- `centrescrx` = 76 (scroll distance)
- `centreydir` = 0 (scroll direction)

---

## Boss Strategies

### Snake Boss (Level 14)
**Three-part battle:**
1. Snake Head (ID 56) - 12 HP
2. Snake Body (ID 57) - 8 HP per segment
3. Snake Turret (ID 58) - 6 HP

**Sounds:** High shriek, low shriek, fire bullet

### Queen Bug (Level 13)
**Attacks:**
- Dripping guts (SFXDRIP)
- Egg spawning
- Worker deployment

**Sound:** Alien shriek on death (SFXQUEENSCREAM)

### Lava Boss (Level 33)
**Behavior:** Rises from lava streams  
**Attack:** Shoots fireballs (SFXFIREBALLS)

### Ultra Boss (Level 54)
**Final boss** with multiple phases  
**Sounds:** Zoom in/out, "BOOOO!", scream, "SCHLOORP"

---

## Boss Sound Catalog

| Sound | Hex | Boss |
|-------|-----|------|
| SFXSNAKEBOSS1 | $AF | Snake (high) |
| SFXSNAKEBOSS2 | $B0 | Snake (low) |
| SFXSNAKEBOSS3 | $B1 | Snake (fire) |
| SFXQUEENSCREAM | $C1 | Queen Bug |
| SFXLAVABOSS | $D9 | Lava Boss |
| SFXPUSSMANBELCH | $CC | Puss Boss |
| SFXMUTOID | $CD | Mutoid Man |
| SFXULTRABOSS | $CD | Ultra Boss |

---

## Password Rewards

Defeating bosses unlocks passwords at specific levels:
- Level 3: Popeye Boss → Password 27
- Level 13: Queen Bug → Password displayed
- Level 14: Snake Boss → Password 20
- Level 31: Ancient Boss → Password displayed
- Level 33: Lava Boss → Password 30
- Level 40: Screen Lifter → Password displayed
- Level 52: Puss Boss → Password 12
- Level 53: Mutoid Man → Password 47
- Level 54: Ultra Boss → Password displayed

---

**Source Citations:**
- Boss list: INITLEVE.A:fightboss
- Mechanics: BOB.A (bossstrength, centrescroll)
- Sounds: EQUATES.H (SFX*BOSS*)
