# **Q2 — Price vs. Sentiment**
# What is the approval ratio (`positive / total ratings`) across price tiers — 
# and does a higher price actually produce better sentiment when you filter out
#  games with fewer than 500 total ratings?
# > Without the rating count filter, one five-star game with 12 reviews skews an 
# entire tier. The filter forces the question to be about games with a real
#  audience, not statistical noise.
# *Primary skills: derived column creation, `pd.cut` for price binning, boolean 
# masking, grouped bar chart*


from pathlib import Path
import pandas as pd

base_path: Path = Path(__file__).resolve().parent.parent
path: Path = base_path / "data" / "cleaned_data.csv"
df: pd.DataFrame = pd.read_csv(path)


MINIMUM_RATING_FILTER = 500
bins = [-0.1, 0.00, 4.99, 9.99, 14.99, 19.99, 29.99, 49.99, 99.99, float('inf')]
labels = [
	"F2P(0.00)",
	"Ultra-Budget(0.1-4.99)", 
	"Budget Indie(5.00-9.99)", 
	"Standard Indie(10.00-14.99)", 
	"Premium Indie(15.00-19.99)", 
	"Mid-Tier(20.00-29.99)", 
	"AA(30.00-49.99)", 
	"AAA+(50.00-99.99)", 
	"AAAA(99.99+)"
	]


filtered_df: pd.DataFrame = df[(df["positive_ratings"] + df["negative_ratings"] > MINIMUM_RATING_FILTER)].copy()

filtered_df['total_review'] = filtered_df["positive_ratings"] + filtered_df["negative_ratings"]
filtered_df['price_tier'] = pd.cut(filtered_df['price'], bins=bins, labels=labels, include_lowest=True)

# Aggregation
# Note: groupby().agg() returns a DataFrame when reset_index() is called
grped_df: pd.DataFrame = filtered_df.groupby("price_tier", observed=True).agg({
    'appid': 'count',
    'average_playtime': 'mean',
    'median_playtime': 'median',
    'positive_ratings': 'sum',
    "total_review": "sum"
}).rename(columns={'appid': 'total_games'}).reset_index()

grped_df = grped_df.assign(
    gap = grped_df["total_review"] - grped_df["positive_ratings"],
    ratio = grped_df["positive_ratings"] / grped_df["total_review"]
)

sorted_df: pd.DataFrame = grped_df.sort_values(by="ratio", ascending=False)

print(sorted_df)

# ==============================================================================
# Q2 — CONCLUSIONS: PRICE TIER vs. APPROVAL RATIO
# ==============================================================================
#
# RESULTS (sorted by approval ratio):
#   Budget Indie    ($5–$9.99)   → 0.896  | 849 games  | median playtime 208h
#   Standard Indie  ($10–$14.99) → 0.874  | 807 games  | median playtime 256h
#   Ultra-Budget    ($0.1–$4.99) → 0.846  | 754 games  | median playtime 202h
#   AAA+            ($50–$99.99) → 0.841  |   8 games  | median playtime 194h
#   Premium Indie   ($15–$19.99) → 0.838  | 345 games  | median playtime 266h
#   F2P             ($0.00)      → 0.831  | 614 games  | median playtime  69h
#   Mid-Tier        ($20–$29.99) → 0.744  | 275 games  | median playtime 376h
#   AA              ($30–$49.99) → 0.720  | 170 games  | median playtime 932h
#
# 1. PRICE DOES NOT PREDICT APPROVAL RATIO
#    The data disproves a simple "pay more, get better" relationship.
#    The highest approval ratios belong to the $0–$15 range, not AAA or AA.
#    Beyond $20, approval ratios drop consistently and sharply — Mid-Tier
#    sits at 0.744 and AA at 0.720, both well below even F2P's 0.831.
#
# 2. THE EXPECTATION ASYMMETRY EFFECT
#    The sweet spot ($5–$14.99) benefits from asymmetric player expectations.
#    A player paying $9.99 for an Indie title applies a lower threshold for
#    satisfaction than one paying $39.99 for an AA game. A competent $10 game
#    gets praised; the same quality at $40 gets torn apart. Price signals
#    a quality promise — the higher the price, the harder the promise is
#    to keep. This is the core driver of the ratio inversion above $20.
#
# 3. THE "ABSOLUTE REVIEWER" THRESHOLD
#    Above $20, players shift from casual reviewers to critical evaluators.
#    Mid-Tier and AA buyers are typically genre veterans who know exactly
#    what a polished product looks like and will not overlook rough edges.
#    The ratio cliff between Premium Indie (0.838) and Mid-Tier (0.744)
#    is the sharpest drop in the dataset — 9.4 percentage points — and
#    it maps almost exactly onto the $20 psychological price barrier.
#
# 4. F2P IS NOT A SAFE HARBOR
#    Free to Play sits at 0.831 — below all three Indie tiers. Despite
#    zero financial barrier to entry, F2P games do not earn goodwill.
#    Players engage freely but review critically: aggressive monetization,
#    pay-to-win mechanics, and content drip-feeding are well-understood
#    patterns that the audience penalizes regardless of the $0 entry point.
#    F2P's median playtime of 69h (vs 200h+ for paid Indie) further
#    confirms from Q1: high engagement hours are whale-driven, not broad
#    satisfaction.
#
# 5. AAA+ ($50–$99.99) IS STATISTICALLY UNRELIABLE
#    Only 8 games passed the 500-review filter in this tier. The 0.841
#    ratio looks healthy but is almost certainly dominated by 1–2 heavy
#    hitters with massive rating volumes pulling the aggregate. With n=8,
#    no conclusion about this tier is generalizable. A meaningful AAA+
#    analysis would require a separate dataset with richer premium game
#    coverage.
#
# FINAL VERDICT:
#    The $5–$14.99 range is the approval ratio sweet spot on Steam —
#    not because the games are objectively better, but because the price
#    sets expectations the product can realistically exceed. Above $20,
#    the promise outpaces the delivery for most titles. Below $5 and at
#    $0, the product quality ceiling is lower and players know it.
#    Price on Steam is not a quality signal — it is an expectation contract,
#    and the market punishes contracts that overpromise.
# ==============================================================================