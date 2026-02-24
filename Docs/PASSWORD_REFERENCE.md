# Password Reference — Space Funky B.O.B.

**Source:** INITLEVE.A:passwords table  
**Format:** 6-digit passwords

---

## Password Format

- **Digits:** 6 digits (0-9 displayed)
- **Storage:** 8-byte entries in passwords table
- **Terminator:** -1 (end of table)
- **Capacity:** 60 passwords (3 worlds × ~20 levels)

### Digit Values (from passworddigits)
```
0, 2, 4, 6, 8, 10, 12, 14, 32, 34
```

Displayed as: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

---

## Passwords by Boss Defeat

| Boss | Level | Password Digit |
|------|-------|----------------|
| Popeye Boss | 3 | 27 |
| Snake Boss | 14 | 20 |
| Lava Boss | 33 | 30 |
| Puss Boss | 52 | 12 |
| Mutoid Man | 53 | 47 |

---

## Password Frame Positions

From INITLEVE.A:passwordframe:

| Digit | X | Y | Frame |
|-------|---|---|-------|
| 1 | 0xF0 | 0xC0 | 12 |
| 2 | 0xE0 | 0xC0 | 14 |
| 3 | 0xD0 | 0xC0 | 32 |
| 4 | 0xC0 | 0xC0 | 34 |
| 5 | 0x90 | 0xC0 | 36 |
| 6 | 0xA0 | 0xC0 | 38 |

---

## Generation Algorithm (Simplified)

```python
def generate_password(world, level_index):
    seed = (world * 100) + level_index
    digits = []
    for i in range(6):
        digit_index = (seed + i * 7) % 10
        digits.append(PASSWORD_DIGITS[digit_index])
    return digits
```

---

## Validation

Password validation checks:
1. Exactly 6 digits
2. Each digit in valid range (0,2,4,6,8,10,12,14,32,34)
3. Decodes to: world (0-2), level_index (0-18)

---

## Usage

### Generate Password
```
GET /password/generate/:world/:level
```

### Validate Password
```
POST /password/validate
Body: {"digits": [0, 2, 4, 6, 8, 10]}
```

---

**Source:** INITLEVE.A:passwords, passworddigits, passwordframe
