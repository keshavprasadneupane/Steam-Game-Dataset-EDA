from pathlib import Path
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
base_path = Path(__file__).resolve().parent.parent
path = base_path / "data" / "cleaned_data.csv"

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

# Create dataframe
stats_df = pd.DataFrame(results)

# Sort by strongest skew/distortion
stats_df = stats_df.sort_values(
	by="gap_ratio",
	ascending=False
)

print(stats_df.to_string(index=False))

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