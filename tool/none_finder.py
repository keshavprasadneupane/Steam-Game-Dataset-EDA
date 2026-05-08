import pandas as pd
import sys
import os

def find_null_variants():
    # Check if a filepath was provided in the terminal
    if len(sys.argv) < 2:
        print("Usage: uv run question_1.py <path_to_csv>")
        return

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        return

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Your regex pattern
    null_pattern = r'^(?i)\(?none\)?$|^(?i)\(?null\)?$|^(?i)\(?n/a\)?$|^(?i)\(?na\)?$|^\s*$'

    first_col = df.columns[0]

    print(f"{'TYPE':<15} | {'COLUMN':<15} | {first_col}")
    print("-" * 60)

    for col in df.columns:
        # 1. Native Nulls (NaN/None)
        nan_mask = df[col].isna()
        if nan_mask.any():
            for ref in df.loc[nan_mask, first_col]:
                print(f"{'[Native NAN]':<15} | {col:<15} | {ref}")

        # 2. String Patterns (None, N/A, "", etc.)
        str_mask = df[col].astype(str).str.contains(null_pattern, regex=True, na=False)
        
        # Avoid double-printing the same row if it was already caught as a Native NaN
        str_mask = str_mask & ~nan_mask
        
        if str_mask.any():
            # Using loc for efficiency to grab only matching rows
            subset = df.loc[str_mask, [first_col, col]]
            for _, row in subset.iterrows():
                val = str(row[col])
                # Show empty strings as '' so they aren't invisible
                display_val = f"'{val}'" if val.strip() == "" else val
                print(f"{display_val:<15} | {col:<15} | {row[first_col]}")

if __name__ == "__main__":
    find_null_variants()