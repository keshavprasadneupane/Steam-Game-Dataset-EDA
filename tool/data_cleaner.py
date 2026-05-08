import sys
from pathlib import Path
import pandas as pd

# 1. Setup Paths
base_path = Path(__file__).parent
default_input = base_path / 'data' / 'data.csv'
default_output = base_path / 'data' / 'cleaned_data.csv'

# Check if a path was provided in the terminal, otherwise use hardcoded default
if len(sys.argv) > 1:
    path = Path(sys.argv[1])
    # If a custom path is used, save cleaned file in the same directory
    cleaned_path = path.parent / f"cleaned_{path.name}"
else:
    path = default_input
    cleaned_path = default_output

# 2. Safety Check
if not path.exists():
    print(f"Error: File not found at {path}")
    sys.exit(1)

# 3. Load Data
df = pd.read_csv(path)

# 4. Null Handling
null_replacement_dict = {
    "developer": "Unknown",
    "publisher": "Unknown",
}

# Escaped regex to prevent markdown/parser errors
NULL_PATTERN = (
    r'^(?i)\\(?none\\)?$'
    r'|^\\(?null\\)?$'
    r'|^\\(?n/a\\)?$'
    r'|^\\(?na\\)?$'
    r'|^\\s*$'
)

# Apply targeted string replacement
for column, replacement in null_replacement_dict.items():
    if column in df.columns:
        # Replace string variants and then fill native NaNs
        df[column] = df[column].replace(NULL_PATTERN, replacement, regex=True).fillna(replacement)

# 5. Save Results
df.to_csv(cleaned_path, index=False)
print(f"Success! Cleaned data saved to: {cleaned_path}")