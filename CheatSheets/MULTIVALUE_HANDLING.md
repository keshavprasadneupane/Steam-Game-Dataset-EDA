# 📑 Universal Cheatsheet: Multi-Value Column Handling

Applies to any column that stores multiple values per cell, such as
`"Action;Indie;RPG"` or `"['Action', 'Indie', 'RPG']"`.

All examples below share this starting DataFrame:

| app_id | name | tags | price |
|---|---|---|---|
| 123 | Lost Ark | Action;Indie;RPG | 0.00 |
| 456 | Factorio | Strategy;Simulation | 29.99 |
| 789 | Hades | Action;Indie;Roguelike | 24.99 |

---

## 1. The Mapping Table Strategy ✅ Recommended

Creates a separate "link" table, keeping your main DataFrame lean.
Safe for aggregation because numeric columns are never multiplied.

```python
tags_df = df[['app_id', 'tags']].copy()
tags_df['tags'] = tags_df['tags'].str.split(';')
tags_df = tags_df.explode('tags').reset_index(drop=True)
tags_df['tags'] = tags_df['tags'].str.strip()
```

**Before** — `df` (unchanged, stays 3 rows):

| app_id | name | tags | price |
|---|---|---|---|
| 123 | Lost Ark | Action;Indie;RPG | 0.00 |
| 456 | Factorio | Strategy;Simulation | 29.99 |
| 789 | Hades | Action;Indie;Roguelike | 24.99 |

**After** — new `tags_df` (8 rows, one per tag):

| app_id | tags |
|---|---|
| 123 | Action |
| 123 | Indie |
| 123 | RPG |
| 456 | Strategy |
| 456 | Simulation |
| 789 | Action |
| 789 | Indie |
| 789 | Roguelike |

**Best for:** Tag frequency counts, "find all games with tag X" queries,
and anything you'd express as a SQL JOIN.

---

## 2. One-Hot Encoding (Binary Columns)

Turns every unique tag into its own `0`/`1` column. Makes the table wide,
but enables multi-tag filtering and ML feature vectors in one step.

```python
binary_df = df['tags'].str.get_dummies(sep=';')
df = pd.concat([df, binary_df], axis=1)

indie_strategy = df[(df['Indie'] == 1) & (df['Strategy'] == 1)]
```

**Before:**

| app_id | name | tags |
|---|---|---|
| 123 | Lost Ark | Action;Indie;RPG |
| 456 | Factorio | Strategy;Simulation |
| 789 | Hades | Action;Indie;Roguelike |

**After** — same 3 rows, but now very wide:

| app_id | name | tags | Action | Indie | RPG | Roguelike | Simulation | Strategy |
|---|---|---|---|---|---|---|---|---|
| 123 | Lost Ark | Action;Indie;RPG | 1 | 1 | 1 | 0 | 0 | 0 |
| 456 | Factorio | Strategy;Simulation | 0 | 0 | 0 | 0 | 1 | 1 |
| 789 | Hades | Action;Indie;Roguelike | 1 | 1 | 0 | 1 | 0 | 0 |

**Best for:** Machine learning feature engineering, complex AND/OR filtering.

> ⚠️ **Memory warning:** With 400+ unique Steam tags, `get_dummies` creates
> 400+ columns. Consider filtering to only the tags you care about first.

---

## 3. Primary Tag Extraction

Takes only the first item in the list. Fast and simple, but silently
discards everything after position 0.

```python
df['primary_tag'] = df['tags'].str.split(';').str[0].str.strip()
```

**Before:**

| app_id | tags |
|---|---|
| 123 | Action;Indie;RPG |
| 456 | Strategy;Simulation |
| 789 | Action;Indie;Roguelike |

**After** — one new column, everything else dropped:

| app_id | tags | primary_tag |
|---|---|---|
| 123 | Action;Indie;RPG | Action |
| 456 | Strategy;Simulation | Strategy |
| 789 | Action;Indie;Roguelike | Action |

**Best for:** Pie charts, high-level groupings, cases where tag order is
intentional (e.g., the developer listed the main genre first).

---

## 4. List Transformation (Python-Native)

Keeps the tags as an actual Python list in the cell. Useful for row-level
logic without restructuring the whole DataFrame.

```python
df['tags_list'] = df['tags'].str.split(';').apply(
    lambda x: [t.strip() for t in x] if isinstance(x, list) else []
)

action_games = df[df['tags_list'].apply(lambda x: 'Action' in x)]
multi_tag    = df[df['tags_list'].apply(len) >= 3]
```

**Before:**

| app_id | tags |
|---|---|
| 123 | Action;Indie;RPG |
| 456 | Strategy;Simulation |
| 789 | Action;Indie;Roguelike |

**After** — same rows, new `tags_list` column holds a real Python list:

| app_id | tags | tags_list |
|---|---|---|
| 123 | Action;Indie;RPG | `['Action', 'Indie', 'RPG']` |
| 456 | Strategy;Simulation | `['Strategy', 'Simulation']` |
| 789 | Action;Indie;Roguelike | `['Action', 'Indie', 'Roguelike']` |

`action_games` result (rows where `'Action' in tags_list`):

| app_id | name | tags_list |
|---|---|---|
| 123 | Lost Ark | `['Action', 'Indie', 'RPG']` |
| 789 | Hades | `['Action', 'Indie', 'Roguelike']` |

**Best for:** Conditional row logic, tag counting per row, quick scripts
where restructuring isn't worth it.

---

## 🛠️ Summary Comparison

| Method | Row Count | Column Count | Data Integrity | Use When |
|---|---|---|---|---|
| **Mapping Table** | Increases | Stays same | ✅ Safe | You need to aggregate or query by tag |
| **One-Hot** | Stays same | Increases significantly | ✅ Safe | ML features or AND/OR multi-filter |
| **Primary Only** | Stays same | +1 | ⚠️ Lossy | Quick grouping, tag order is meaningful |
| **List Transform** | Stays same | Stays same | ✅ Safe | Row-level logic, no restructuring needed |
| **Raw `.explode()`** | Increases | Stays same | ❌ Risky | Almost never — use Mapping Table instead |

---

## ⚠️ The Double-Explode Trap

Never call `.explode()` on two different multi-value columns in the same
DataFrame. It produces a Cartesian product that squares your row count and
corrupts every aggregation downstream.

```python
# ❌ WRONG — a game with 3 genres and 3 tags produces 9 rows, not 3
df = df.explode('genres').explode('tags')
```

**What that looks like** for Lost Ark (`genres: Action;RPG`, `tags: Indie;Online`):

| app_id | name | genres | tags |
|---|---|---|---|
| 123 | Lost Ark | Action | Indie |
| 123 | Lost Ark | Action | Online |
| 123 | Lost Ark | RPG | Indie |
| 123 | Lost Ark | RPG | Online |

Every numeric column (price, playtime, owners) now appears 4× — your
`sum()` is 4× too large, your `mean()` is correct by accident, and the
damage is silent.

```python
# ✅ RIGHT — explode each into its own separate link table
genres_df = df[['app_id', 'genres']].explode('genres').reset_index(drop=True)
tags_df   = df[['app_id', 'tags']].explode('tags').reset_index(drop=True)
```

**Result** — two clean, independent tables you JOIN only when needed:

`genres_df`:

| app_id | genres |
|---|---|
| 123 | Action |
| 123 | RPG |

`tags_df`:

| app_id | tags |
|---|---|
| 123 | Indie |
| 123 | Online |