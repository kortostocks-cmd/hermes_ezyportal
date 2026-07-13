# Stupefy Dedup Gap — Jun 30 2026

## The Bug
During a bulk create from `plantas_nuevas` → portal + INVENTARIO sheet:

1. **Step 1 (dedup check)**: Script checked portal names, found 47 that already existed, and skipped them (correct).
2. **Step 2 (create)**: Created 44 truly-new items in portal (correct).
3. **Step 3 (append to INVENTARIO)**: Only appended the 44 new items to the INVENTARIO sheet (WRONG).

**Result**: 47 plants that already existed in the portal were **never added to the INVENTARIO sheet**, leaving the sheet with only 118 original + 44 new = 162 rows instead of 162 + 47 = 209 rows.

## Root Cause
The dedup-check script (`stupefy_step1.py`) correctly identified `skip_list` and `create_list`, but the "append to sheet" step only processed `create_list`. The skip-list items were silently dropped with no sheet update.

The user noticed when they looked at the sheet and saw missing plants like ANTORCHA, LIRIO, PALMA DRACAENA, etc.

## Fix
After creating items in the portal, ALSO append the skip-list names to the target sheet (INVENTARIO). The skip-list items already have portal entries, they just need sheet rows.

```python
# After creating new items, also add skipped (existing) items to sheet:
all_new_rows = []
for codigo, nombre, _, _ in create_list:
    all_new_rows.append([nombre, '', 0, ''])
for _, nombre, _, _ in skip_list:
    all_new_rows.append([nombre, '', 0, ''])

# Sort all, write to sheet
```

## Prevention
In any stupefy-style workflow (sheet → portal):

1. **Dedup phase** produces two lists: `to_create` (new) and `to_add_to_sheet` (existing-in-portal, missing-from-sheet).
2. **Create phase** sends `to_create` to portal API.
3. **Sheet phase** appends BOTH lists to the target sheet tab.
4. **Always** re-check by reading the sheet back and reporting row count to the user.

## Sheet Stats After Fix
- INVENTARIO: 210 rows (header + 209 data rows)
- 118 original + 44 new + 47 skipped-but-added = 209 total