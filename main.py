from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

file_path = Path(__file__).parent /"data"/"cleaned_data.csv"

df = pd.read_csv(file_path)

df_copy:pd.DataFrame = df.copy()
# preparing the datas.

df_copy[["owners_lb", "owner_ub"]] = df_copy["owners"].str.split("-", expand=True).astype(int)
df_copy["owners_avg"] = (df_copy["owners_lb"] + df_copy["owner_ub"]) * 0.5

# speration of values in hot encoaded path since unique genre are only 39.
genre_dummies = df_copy['genres'].str.get_dummies(sep=';')
total_genres = len(genre_dummies.columns)


df_final:pd.DataFrame = pd.concat([df_copy, genre_dummies], axis=1)

all_features = ["price","owners_avg"]+ list(genre_dummies.columns)

corr_matrix :pd.DataFrame= df_final[all_features].corr()
sale_corr = corr_matrix["owners_avg"].sort_values(ascending=False).drop("owners_avg")


print(len(df))
print(sale_corr)




plot_data = sale_corr

# 2. Setup the Plot
plt.figure(figsize=(12, 7))
colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in plot_data.values]

# 3. Create Horizontal Bar Chart
bars = plt.barh(plot_data.index, plot_data.values, color=colors)

# 4. Add the actual correlation numbers to the end of the bars
for bar in bars:
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2, 
             f' {width:.4f}', 
             va='center', fontsize=10, fontweight='bold')

# 5. Styling
plt.title('Impact on Sales (Correlation with owners_avg)', fontsize=16, pad=20)
plt.xlabel('Correlation Coefficient (Strength)', fontsize=12)
plt.axvline(0, color='black', linewidth=0.8) # Add a vertical line at 0
plt.gca().invert_yaxis() # Highest correlation at the top
plt.grid(axis='x', linestyle='--', alpha=0.3)
plt.tight_layout()

# 6. Display
plt.show()