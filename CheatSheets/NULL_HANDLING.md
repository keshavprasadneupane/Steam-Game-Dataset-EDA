# 🛠️ Universal Data Null-Handling Cheatsheet

## The Discovery Phase: "The Null Hunter"

Before cleaning, you must identify *how* `None` is represented. It is rarely just
one thing — it is often a mix of native `NaN` objects and various string typos.

```python
import pandas as pd

# Uses [()] character classes instead of \( \) to avoid LaTeX parser conflicts.
# Functionally identical regex — [(]? means "optional literal (" without \(.
NULL_PATTERN = (
    r'(?i)^[(]?none[)]?$'
    r'|^[(]?null[)]?$'
    r'|^[(]?n/a[)]?$'
    r'|^[(]?na[)]?$'
    r'|^\s*$'
)

def find_all_null_types(df: pd.DataFrame) -> None:
    """Scan every column and print rows containing any null variant."""
    for col in df.columns:
        nan_mask = df[col].isna()
        str_mask = df[col].astype(str).str.contains(NULL_PATTERN, regex=True, na=False)
        matches = df[nan_mask | str_mask]

        if not matches.empty:
            print(f"\n--- Column: '{col}' ({len(matches)} suspect rows) ---")
            for _, row in matches.iterrows():
                print(f"  Value: {repr(row[col])}  |  Row ID: {row.iloc[0]}")

find_all_null_types(df)
```

---

## Targeted String Replacement (Categorical / Object Columns)

> **⚠️ Important:** Only apply string-based replacement to `object`/`string` dtype
> columns. Applying regex replace to a numeric column will silently coerce it to
> `object`, corrupting downstream math.

**Goal:** Unify `"n/a"`, `"None"`, `""`, and native `NaN` into a single `"Unknown"` label.

```python
target_cols = ['category_name', 'user_feedback', 'supplier_status']

for col in target_cols:
    df[col] = (
        df[col]
        .replace(NULL_PATTERN, "Unknown", regex=True)
        .fillna("Unknown")
    )
```

---

## Numeric Handling (Math-Safe Methods)

Numeric columns require statistical filling to preserve calculation integrity.

| Method | Best Used For | Pandas Snippet |
|---|---|---|
| **Median** | Skewed data (price, salary) | `df[col].fillna(df[col].median())` |
| **Mean** | Normally distributed data | `df[col].fillna(df[col].mean())` |
| **Zero** | Counts, quantities | `df[col].fillna(0)` |
| **Sentinel `-1`** | Codes, ages — flags missing explicitly | `df[col].fillna(-1)` |

---

## Automated Universal Strategy

This loop processes an entire DataFrame safely by checking `dtype` before deciding
fill logic.

```python
for col in df.columns:
    if df[col].dtype == 'object':
        # Text columns: collapse all null variants into "Unknown"
        df[col] = (
            df[col]
            .replace(NULL_PATTERN, "Unknown", regex=True)
            .fillna("Unknown")
        )
    else:
        # Numeric columns: median fill keeps distributions stable
        df[col] = df[col].fillna(df[col].median())
```

---

## Quick Verification

Never assume cleaning worked. Run these three checks after every pass:

```python
# 1. Count remaining native nulls per column
print(df.isna().sum())

# 2. Confirm no numeric columns silently became object
print(df.dtypes)

# 3. Audit unique values in a cleaned text column
print(df['category_name'].value_counts(dropna=False))
```

> **What to look for:** Any column that was `int64`/`float64` and is now `object`
> means your regex replace accidentally touched it. Re-check your `target_cols` list.