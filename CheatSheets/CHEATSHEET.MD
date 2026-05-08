Here is the refined, high-performance **Pandas Combat Checksheet** formatted specifically for your Markdown files. It’s organized to follow the logical flow of a data project: **Load → Clean → Transform → Analyze**.

---

# 🐼 Pandas Combat Checksheet

### 1. Data Ingestion & Health Check
*Before analysis, you must verify the "integrity" of your data.*

| Function | Description | Pro-Tip |
| :--- | :--- | :--- |
| `pd.read_csv()` | Load local data. | Use `low_memory=False` for large Steam datasets. |
| `df.info()` | Check dtypes & nulls. | **Crucial** to see if "Price" is an object (string) or float. |
| `df.describe()` | Statistical summary. | Use `include='all'` to see stats for non-numeric columns. |
| `df.shape` | `(rows, columns)`. | Use this to verify data hasn't "leaked" after a join. |
| `df.memory_usage()` | Memory per column. | Helps optimize performance on older hardware. |

---

### 2. Selection & Boolean Masking
*The "Search Engine" of Pandas. Essential for filtering top-rated or free games.*



*   **Single Column:** `df['price']`
*   **Multiple Columns:** `df[['name', 'price', 'rating']]`
*   **Simple Filter:** `df[df['price'] == 0]` (Finds all Free-to-Play games)
*   **Complex Filter (The Mask):**
    ```python
    # Logic: Released after 2020 AND rating over 90%
    mask = (df['year'] > 2020) & (df['rating'] > 90)
    top_new_games = df[mask]
    ```
*   **String Search:** `df[df['genre'].str.contains('Indie', na=False)]`

---

### 3. Data Cleaning (The "Janitor" Phase)
*Steam data often has missing descriptions or malformed price strings.*

| Task | Code |
| :--- | :--- |
| **Check Nulls** | `df.isnull().sum()` |
| **Drop Missing** | `df.dropna(subset=['price'])` |
| **Fill Missing** | `df['desc'].fillna('No description')` |
| **Change Type** | `df['price'] = df['price'].astype(float)` |
| **Rename Cols** | `df.rename(columns={'positive_ratings': 'pos_rev'}, inplace=False)` |
| **Drop Column** | `df.drop(columns=['unnecessary_col'])` |

---

### 4. Transformation & Aggregation
*This is how you answer: "Which genre has the highest playtime?"*



**The GroupBy Pattern:**
```python
# Format: df.groupby('Category')['Value'].MathFunction()
genre_playtime = df.groupby('genre')['playtime'].mean()
```

**Common Aggregations:**
*   `.mean()`, `.median()`, `.sum()`, `.count()`
*   `.nlargest(5)` — Quickly get the Top 5.
*   `.value_counts()` — Get a frequency count (e.g., how many games per developer).
*   `.agg(['min', 'max', 'std'])` — Multiple stats at once.

---

### 5. Reshaping & Merging
*Used when you add a second dataset like "Tags" or "Reviews".*

| Method | SQL Equivalent | Usage |
| :--- | :--- | :--- |
| `pd.merge(on='id')` | **JOIN** | Connect two tables using a common key (e.g., `appid`). |
| `pd.concat()` | **UNION** | Stack two dataframes on top of each other. |
| `df.explode('genre')` | **N/A** | If one row has "Action;RPG", this splits it into two separate rows. |

---

### 6. Vectorized Operations (Math)
*Never use `for` loops in Pandas. Use vectorization.*

*   **Basic Math:** `df['revenue'] = df['price'] * df['owners']`
*   **Conditional Math:** 
    ```python
    import numpy as np
    # If price is 0, label 'Free', else 'Paid'
    df['type'] = np.where(df['price'] == 0, 'Free', 'Paid')
    ```

---

### 7. Fast Visualization
*To verify distributions while coding in your `.py` script.*

*   **Histogram:** `df['price'].hist(bins=50)`
*   **Scatter Plot:** `df.plot.scatter(x='price', y='playtime')`
*   **Bar Chart:** `df['genre'].value_counts().plot(kind='bar')`

---

### ⚠️ Common Errors to Avoid
1.  **SettingWithCopyWarning:** Occurs when you try to modify a slice of a dataframe. **Solution:** Use `.copy()` when creating a filtered dataframe.
    *   *Bad:* `new_df = df[df['price'] > 0]` 
    *   *Good:* `new_df = df[df['price'] > 0].copy()`
2.  **Inplace Deprecation:** Avoid `inplace=True`. It is being removed from future Pandas versions. Always re-assign: `df = df.dropna()`.
3.  **Data Alignment:** Ensure your indices match before adding columns from different dataframes.
```