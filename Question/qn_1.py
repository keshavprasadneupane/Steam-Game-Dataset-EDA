from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# ============================================================
# Q1 — Genre Engagement Analysis
#
# Which genres have the highest average playtime,
# and how far does the average median fall from
# the average mean within those genres?
#
# Interpretation:
# Steam already provides per-game average and median
# playtime values.
#
# Therefore:
# - mean_playtime   = mean of game averages
# - median_playtime = mean of game medians
#
# A large gap between them suggests that a small
# number of highly dedicated players are inflating
# the overall average engagement.
# ============================================================

FILTER_PLAYTIME: int = 2
MIN_GAMES: int = 30

# Load dataset
root_path = Path(__file__).resolve().parent.parent
path = root_path / "data" / "cleaned_data.csv"
save_file_path = root_path/ "output_picture"



df:pd.DataFrame = pd.read_csv(path)

# Remove near-zero playtime rows
filtered_df: pd.DataFrame = df[
	(df["average_playtime"] > FILTER_PLAYTIME)
	& (df["median_playtime"] > FILTER_PLAYTIME)
].copy()

# Get all unique genres
all_genres = sorted(
	filtered_df["genres"]
	.str.split(";")
	.explode()
	.dropna()# data is already cleaned.
	.unique()
)

results = []

print("\n--- Genre Engagement Analysis ---")
print("mean_playtime   : Mean of game average playtimes")
print("median_playtime : Median of game median playtimes")
print("gap_ratio       : Mean / Median distortion")
print("std_dev         : Engagement variability\n")

for genre in all_genres:
    subset: pd.DataFrame = filtered_df[
        filtered_df["genres"].str.contains(
           genre,
            regex=True,
            na=False
        )
    ]

    game_count = len(subset)

    # Filter out niche genres with low sample sizes to ensure statistical significance
    if game_count < MIN_GAMES:
        continue

    # ========================================================
    # Core Metrics
    # ========================================================
    # mean_playtime: The average of the averages
    mean_val = subset["average_playtime"].mean()

    # median_playtime: The median of the medians (the "middle" player)
    med_val = subset["median_playtime"].median()

    gap = mean_val - med_val
    gap_ratio = mean_val / med_val if med_val != 0 else 0
    std_dev = subset["average_playtime"].std()

    results.append({
        "genre": genre,
        "mean_playtime": round(mean_val, 2),
        "median_playtime": round(med_val, 2),
        "gap": round(gap, 2),
        "gap_ratio": round(gap_ratio, 2),
        "std_dev": round(std_dev, 2),
        "game_count": game_count
    })



stats_df = pd.DataFrame(results)

# Sort by strongest skew/distortion
stats_df = stats_df.sort_values(
	by="gap_ratio",
	ascending=False
)

print(stats_df.to_string(index=False))

stats_df = stats_df.sort_values(by="gap_ratio", ascending=True)

# 1. Setup the figure and primary axes
fig, ax1 = plt.subplots(figsize=(12, 8), dpi=100)

# Define bar positions and width
y_indices = np.arange(len(stats_df))
bar_width = 0.35

# 2. Plot Bars (Mean vs Median Playtime)
rects1 = ax1.barh(y_indices + bar_width/2, stats_df['mean_playtime'], bar_width, 
                 label='Mean Playtime', color='#3182bd', alpha=0.9)
rects2 = ax1.barh(y_indices - bar_width/2, stats_df['median_playtime'], bar_width, 
                 label='Median Playtime', color='#de2d26', alpha=0.9)

# Labels and styling for primary axis
ax1.set_xlabel('Playtime (Hours)', fontsize=12, fontweight='bold', labelpad=10)
ax1.set_ylabel('Genres', fontsize=12, fontweight='bold')
ax1.set_yticks(y_indices)
ax1.set_yticklabels(stats_df['genre'], fontsize=11)
ax1.set_title('Genre Engagement & Distortion Analysis\n(Comparison of Mean vs Median Playtime and Skew Ratio)', 
             fontsize=14, fontweight='bold', pad=20)
ax1.grid(axis='x', linestyle='--', alpha=0.5)

# 3. Plot Line on Secondary Axis (Gap Ratio / Distortion)
ax2 = ax1.twiny()  # Create a twin axis sharing the y-axis
line = ax2.plot(stats_df['gap_ratio'], y_indices, color="#483C3C", 
                marker='o', linewidth=2, markersize=6, label='Gap Ratio (Distortion)')

# Labels and styling for secondary axis
ax2.set_xlabel('Gap Ratio (Mean / Median)', color='#e6550d', fontsize=12, fontweight='bold', labelpad=10)
ax2.tick_params(axis='x', labelcolor='#e6550d')
ax2.spines['top'].set_color('#e6550d')
ax2.spines['top'].set_linewidth(1.5)

# 4. Combine Legends
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='lower right', frameon=True, facecolor='white', edgecolor='none')

# Tight layout adjustments to prevent text cutting off
plt.tight_layout()

# 5. Save and Display
# Using your script's save path variable:
plt.savefig(save_file_path / "q1_genre_engagement_analysis.png", bbox_inches='tight')
plt.show()






# ==============================================================================
# Q1 — CONCLUSIONS: GENRE ENGAGEMENT & DISTORTION
# ==============================================================================
#
# 1. THE "ENGAGEMENT TRAP" (HIGH SKEW):
#    Free to Play and Massively Multiplayer are "Whale-driven."
#    - Free to Play (621 games) has a gap_ratio of 24.94 — the highest by far.
#      While the mean is 1,521h, the typical player (median) only stays for 61h.
#      The std_dev of 9,876h confirms this is not variance around a central
#      tendency — it is a power-law distribution where a tiny fraction of
#      hyper-dedicated players carry the entire average.
#    - Massively Multiplayer (298 games) has a std_dev of 5,768h — high, but
#      the story is different. The variance here reflects game lifecycle: a dead
#      MMO collapses to near-zero hours, a live one accumulates thousands. The
#      spread is coming from which games survived, not player behavior within them.
#    - In both genres the mean is a vanity metric. The median is the honest number.
#
# 2. HIGH-STABILITY ENGAGEMENT (TRUE RETENTION):
#    RPG (1,167 games), Strategy (1,270 games), and Simulation (1,016 games)
#    are the most statistically trustworthy high-engagement genres.
#    - All three maintain median_playtime of 250–280h across large samples,
#      meaning this is not driven by a handful of outliers.
#    - std_devs of 4,447h, 3,565h, and 2,684h are high in absolute terms but
#      proportionally reasonable given their mean values — and critically, their
#      gap_ratios of 3.12–3.65 confirm the typical player experience closely
#      tracks the reported mean.
#
# 3. NICHE CONSISTENCY:
#    Adult/Niche genres — Gore (94 games), Nudity (76), Sexual Content (60) —
#    have the lowest distortion (gap_ratio < 1.4) and the tightest std_devs
#    in the dataset: 381h, 399h, and 282h respectively.
#    - Small sample sizes mean these conclusions carry less weight, but the
#      pattern is clear: player behavior is highly predictable, few super-users
#      exist, and the mean accurately reflects almost every player's experience.
#
# 4. VOLATILITY IN MASS MARKETS:
#    Indie (3,911 games) and Adventure (2,218 games) have std_devs of 3,180h
#    and 5,108h respectively — and unlike FTP, these are not driven by whales.
#    - With nearly 4,000 and 2,200 titles, that variance is real and structural.
#      A few viral titles sit at the top while thousands of sub-$5 games have
#      near-zero playtime. The large game count confirms this is a market
#      pattern, not a sampling artifact.
#    - Action (2,984 games, std_dev 1,969h) by contrast shows that mass-market
#      genres can achieve scale without the same hit-or-miss volatility —
#      its tighter spread suggests more consistent baseline engagement.
#
# FINAL VERDICT:
# RPG and Strategy offer the deepest, most consistent player commitment —
# large sample sizes (1,000+ games each) and moderate std_devs make this
# conclusion reliable. Free to Play leads in raw hours logged (mean 1,521h)
# but its std_dev of 9,876h and median of just 61h expose the reality:
# the mean is carried by a power-law minority. The median is what the
# market actually delivers to most players.
# ==============================================================================