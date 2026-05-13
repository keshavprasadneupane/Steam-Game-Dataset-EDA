# **Q3 — Platinum Tier Over Time**
# Goal: Analyze the volume and median quality of "Platinum" games (90%+ ratio)
# relative to total Steam releases to determine if Steam Direct (2017)
# diluted the high-end market.
from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd

base_path: Path = Path(__file__).resolve().parent.parent
path: Path = base_path / "data" / "cleaned_data.csv"

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



# graph


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))


ax1.bar(merge_sorted.index, merge_sorted["total_releases_total"], color='skyblue', label="Total Steam Releases")
ax1.set_title("Total Game Releases per Year", fontsize=14, fontweight='bold')
ax1.set_ylabel("Count of Games")
ax1.grid(axis='y', linestyle='--', alpha=0.7)
ax1.axvline(x=2017, color='red', linestyle='--', label="Steam Direct (2017)")
ax1.legend()

ax2.plot(merge_sorted.index, merge_sorted["platinum_market_share"], color='gold', marker='o', linewidth=3, markersize=8)
ax2.set_title("Platinum Market Share %: 'Quality Density' Over Time", fontsize=14, fontweight='bold')
ax2.set_ylabel("Market Share Percentage (%)")
ax2.set_xlabel("Year")

ax2.set_ylim(0, 40) 
ax2.grid(axis='y', linestyle='--', alpha=0.7)

ax2.annotate('Market Saturation Begins', xy=(2014, 7), xytext=(2008, 20),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.tight_layout()
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