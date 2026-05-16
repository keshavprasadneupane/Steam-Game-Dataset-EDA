# **Q3 — Platinum Tier Over Time**
# Goal: Analyze the volume and median quality of "Platinum" games (90%+ ratio)
# relative to total Steam releases to determine if Steam Direct (2017)
# diluted the high-end market.
from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd

root_path: Path = Path(__file__).resolve().parent.parent
path: Path = root_path / "data" / "cleaned_data.csv"
save_file_path = root_path/ "output_picture"


APPROVAL_RATING_RATIO_FILTER = 0.9
MINIMUM_RATING_FILTER = 500
FILTER_YEAR = 2003

df: pd.DataFrame = pd.read_csv(path, parse_dates=["release_date"])
df = df[df["release_date"].dt.year >= FILTER_YEAR]

def get_total_rating(dataframe: pd.DataFrame):
    return dataframe["positive_ratings"] + dataframe["negative_ratings"]

def get_rating_ratio(dataframe: pd.DataFrame):
    return dataframe["positive_ratings"] / get_total_rating(dataframe)

# filter ready.
filtered_df: pd.DataFrame = df[(get_total_rating(df) >= MINIMUM_RATING_FILTER) &
                               (get_rating_ratio(df) >= APPROVAL_RATING_RATIO_FILTER)].copy()

filtered_df["rating_ratio"] = get_rating_ratio(filtered_df)

by_year: pd.Series = df.groupby(df["release_date"].dt.year)["appid"].count().rename("total_releases")
platimun_by_year: pd.Series = filtered_df.groupby(filtered_df["release_date"].dt.year)["appid"].count().rename("total_releases")

merge_sorted = pd.merge(platimun_by_year, by_year, on="release_date", how='left', suffixes=("_platinum", "_total"))

# --- Convert to Percentage ---
merge_sorted["platinum_market_share"] = (merge_sorted["total_releases_platinum"] / merge_sorted["total_releases_total"]) * 100

print(merge_sorted)




#0--------------------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
# 1. Filter for a relevant decade window leading up to the 2019 cutoff
plot_df = merge_sorted.loc[2010:2019]

# 2. Initialize the dual-axis plot
fig, ax1 = plt.subplots(figsize=(12, 7), dpi=100)

# 3. Plot Total Steam Releases (Primary Y-Axis)
color_total = '#b3cde3'  # Soft muted blue
ax1.bar(plot_df.index, plot_df["total_releases_total"], 
        color=color_total, alpha=0.75, width=0.6, label="Total Steam Releases")

ax1.set_xlabel("Year of Release", fontsize=12, fontweight='bold', labelpad=12)
ax1.set_ylabel("Total Volume of Game Releases", color='#4f5b66', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#4f5b66')
ax1.set_xticks(plot_df.index)  # Show every year clearly
ax1.grid(axis='y', linestyle='--', alpha=0.3)

# 4. Plot Platinum Market Share (Secondary Y-Axis)
ax2 = ax1.twiny() # Using twinx to overlay over the same X axis
ax2 = ax1.twinx() 
color_plat = '#d95f02'  # Accent orange

ax2.plot(plot_df.index, plot_df["platinum_market_share"], 
         color=color_plat, marker='o', linewidth=3, markersize=8, 
         label="Platinum Market Share %")

ax2.set_ylabel("Platinum Market Share (% of Total Market)", color=color_plat, fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=color_plat)

# Tighten the limits based strictly on the 2010-2019 data variance
# This prevents the line from flattening out at the bottom
min_share = plot_df["platinum_market_share"].min()
max_share = plot_df["platinum_market_share"].max()
ax2.set_ylim(max(0, min_share * 0.8), max_share * 1.2)
ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.1f}%'))

# 5. Draw the 2017 Steam Direct Line directly through the center of our window
ax1.axvline(x=2017, color='#d62728', linestyle='--', linewidth=2.5, 
            label="Steam Direct Policy (2017)")

# 6. Title and Legend
plt.title("Impact of Steam Direct (2017) on High-End Market Share\nData Snapshot: 2010 – 2019 Cutoff", 
          fontsize=14, fontweight='bold', pad=20)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, facecolor='white')

plt.tight_layout()

# Save the focused snapshot
plt.savefig(save_file_path / "q3_platinum_tier_2019_cutoff_analysis.png", bbox_inches='tight')
plt.show()


# =================================================================================================
# OBSERVATION: MARKET DILUTION & THE TRANSITION TO STEAM DIRECT
# =================================================================================================
#
# THE 500-RATING FILTER RATIONALE:
# To ensure data integrity, this analysis applies a MINIMUM_RATING_FILTER = 500. 
# Any game with fewer than 500 total ratings is considered "insignificant" in the context 
# of the broader market; these titles represent "super-niche" products that do not impact 
# the general consumer experience or the "Platinum" market tier.
#
# 1. THE ALGORITHMIC SHIFT (2014):
# We observe the first major "downhill" jump in quality density in 2014.
#   - THE DATA: Game releases surged from 418 to 1,555 (a 3x increase), while the 
#     Platinum market share dropped from 14% to 7% (a 50% decline in quality density).
#   - THE CAUSE: This jump is attributed to Valve’s implementation of the Discovery Algorithm. 
#     Developers began flooding the platform to leverage algorithmic recommendations.
#   - INSIGHT: During this period, Steam Greenlight was still active, but developers 
#     prioritized "visibility through the algorithm" over the traditional community 
#     voting process, indicating that algorithmic reach had become more valuable than 
#     community curation.
#
# 2. THE STEAM DIRECT EXPLOSION (2017):
# A second, more drastic decline occurred in 2017 following the launch of Steam Direct.
#   - THE DATA: Releases jumped from 4,361 to 6,357, causing the Platinum share to 
#     drop again by nearly 50% (from 4.2% to 2.1%). By 2018, volume peaked at 8,160 
#     games, while the Platinum share shriveled to just 1.5%.
#   - THE CAUSE: Steam Direct removed the "Player Vote" friction of Greenlight. 
#     Without a community filter, the market became saturated with a vast volume of 
#     games that met the entry fee but failed to reach the "Platinum" threshold.
#
# 3. DATA LIMITATIONS (2019):
# The year 2019 is partially omitted from the conclusion. Because our filter requires 
# 500 ratings, newer games from 2019 have not had sufficient time to accumulate the 
# necessary review volume. However, the partial data suggests the downward trend 
# of quality density continues.
#
# FINAL CONCLUSION:
# With 90% confidence, I can conclude that Steam's evolution (the Discovery Algorithm 
# and Steam Direct) has led to a saturated market. While the absolute number of 
# "Platinum" games increases slightly each year, this growth is insignificant 
# compared to the overwhelming volume of total releases. Consequently, the 
# Platinum Market Share is in a state of consistent yearly decline, proving that 
# as the market opens up, high-density quality is being replaced by high-volume noise.
# =================================================================================================