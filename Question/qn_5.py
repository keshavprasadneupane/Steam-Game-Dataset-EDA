# **Q5 — Developer Revenue Efficiency**
# Who are the top 10 developers by estimated gross revenue (`price × owners_avg`),
#  and how does their approval ratio compare to the platform average?
# > High revenue with a below-average approval ratio flags a developer who sells well on
# marketing but underdelivers on product. High revenue with a strong ratio is the 
# actual target benchmark.

from pathlib import Path
from typing import Any
import pandas as pd

SHOWN_DEV =20

# --- Data Loading ---
root_path: Path = Path(__file__).resolve().parent.parent
path: Path = root_path / "data" / "cleaned_data.csv"
save_file_path = root_path/ "output_picture"

df: pd.DataFrame = pd.read_csv(path, parse_dates=["release_date"])

# --- Helper Functions ---
def get_total_rating(dataframe: pd.DataFrame):
	return dataframe["positive_ratings"] + dataframe["negative_ratings"]

def get_rating_ratio(dataframe: pd.DataFrame):
	return dataframe["positive_ratings"] / get_total_rating(dataframe)

# --- Preprocessing ---
copy_df: pd.DataFrame = df.copy()
copy_df = copy_df[(copy_df["average_playtime"] >= 2) & 
				 (get_total_rating(copy_df) >= 500) & 
				 (copy_df["price"] > 0)]

copy_df["approval_ratio"] = get_rating_ratio(copy_df)

copy_df[["owners_lb", "owner_ub"]] = copy_df["owners"].str.split("-", expand=True).astype(int)
copy_df["average_owners"] = (copy_df["owners_lb"] + copy_df["owner_ub"]) * 0.5
copy_df["revenue"] = copy_df["average_owners"] * copy_df["price"]

total_developers = copy_df["developer"].str.split(";").explode().unique()
global_average = copy_df["approval_ratio"].mean()
global_median = copy_df["approval_ratio"].median()

print(f"global mean = {global_average}, median={global_median}")
# --- Classes & Configuration ---
class Config:
	def __init__(self, total: bool, mean: bool, median: bool, std_dev: bool):
		self.total = total
		self.mean = mean
		self.median = median
		self.std_dev = std_dev

class Result:
	def __init__(self, config: Config, postfix: str, subset: pd.DataFrame, field_name: str):
		self.postfix = postfix
		self.total = subset[field_name].sum() if config.total else None
		self.average = subset[field_name].mean() if config.mean else None 
		self.median = subset[field_name].median() if config.median else None 
		self.std_dev = subset[field_name].std() if config.std_dev else None 

	def to_dict(self, is_owner: bool = False) -> dict[str, Any]:
		total_name = "average" if is_owner else "total"
		res = {
			f"{total_name}_{self.postfix}": self.total,
			f"mean_{self.postfix}": self.average,
			f"median_{self.postfix}": self.median,
			f"std_dev_{self.postfix}": self.std_dev,
		}
		return {k: v for k, v in res.items() if v is not None}

owner_config = Config(total=True, mean=False, median=True, std_dev=False)
revenue_config = Config(total=True, mean=True, median=True, std_dev=True)
approval_config = Config(total=False, mean=True, median=True, std_dev=True)

def get(dataframe: pd.DataFrame, developer: str):
	subset: pd.DataFrame = dataframe[dataframe["developer"].str.contains(developer, na=False, regex=False)]
	
	total_games = int(subset["appid"].count())
	if total_games == 0:
		return {}, 0.0

	owner_result = Result(owner_config, "owner", subset, "average_owners")
	revenue_result = Result(revenue_config, "revenue", subset, "revenue")
	approval_result = Result(approval_config, "approval", subset, "approval_ratio")
	
	res = {"total_games": total_games}
	res.update(owner_result.to_dict(True))
	res.update(revenue_result.to_dict())
	res.update(approval_result.to_dict())
	
	total_rev = float(revenue_result.total) if revenue_result.total is not None else 0.0
	return res, total_rev

# --- Main Logic ---
result = []
for dev in total_developers:
	if not isinstance(dev, str): 
		continue
	
	q_dict, final_rev = get(copy_df, dev)
	if final_rev <= 0.0: 
		continue
		
	query_res: dict[str, Any] = {"developer": dev}
	query_res.update(q_dict)
	result.append(query_res)

final_df = pd.DataFrame(result)
final_df = final_df.fillna(0)


# Normalize values for shared-priority sorting
rev_min, rev_max = final_df["total_revenue"].min(), final_df["total_revenue"].max()
app_min, app_max = final_df["median_approval"].min(), final_df["median_approval"].max()

# Avoid division by zero if all values are the same
rev_range = (rev_max - rev_min) if rev_max != rev_min else 1
app_range = (app_max - app_min) if app_max != app_min else 1

final_df["rank_score"] = (
	((final_df["total_revenue"] - rev_min) / rev_range) + 
	((final_df["median_approval"] - app_min) / app_range)
)

sorted_df = final_df.sort_values("rank_score", ascending=False).reset_index(drop=True)

print(f"\n--- Top {SHOWN_DEV} Developers by Revenue Efficiency (Ranked by Total Revenue + Approval Ratio) ---")
print(sorted_df.head(SHOWN_DEV))







# --- Visualization for Top 20 ---
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from pathlib import Path

# 1. Clean the data
top_20 = sorted_df.head(20).copy()
top_20['developer'] = top_20['developer'].apply(
    lambda x: ''.join([i if ord(i) < 128 else '' for i in x]).strip()
)
top_20 = top_20.reset_index(drop=True)

plt.style.use('ggplot')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 18))

# --- Graph 1: Revenue vs Approval Ratio with per-developer color ---
num_devs = len(top_20)
cmap_devs = matplotlib.colormaps.get_cmap('tab20')
dev_colors = [cmap_devs(i / num_devs) for i in range(num_devs)]

rng = np.random.default_rng(42)

scatter_order = top_20.sort_values('total_games', ascending=False)

games_min = scatter_order['total_games'].min()
games_max = scatter_order['total_games'].max()
games_range = (games_max - games_min) if games_max != games_min else 1

for _, row in scatter_order.iterrows():
    i = row.name
    jitter_x = rng.uniform(-0.015, 0.015)

    normalized_size = (row['total_games'] - games_min) / games_range
    altitude_offset = (1 - normalized_size) * 0.02

    ax1.scatter(
        row['total_revenue'] / 1e9 + jitter_x,
        row['median_approval'] + altitude_offset,
        s=row['total_games'] * 60,
        color=dev_colors[i],
        alpha=1.0,
        edgecolors="black",
        linewidths=1.5,
        zorder=3 + (1 - normalized_size) * 20
    )

ax1.axhline(global_average, color='blue', linestyle='--', linewidth=2,
            label=f'Global Mean ({global_average:.2f})', zorder=100)
ax1.axhline(global_median, color='purple', linestyle='-.', linewidth=2,
            label=f'Global Median ({global_median:.2f})', zorder=100)

ax1.set_title('Top 20 Developer Efficiency vs. Global Benchmarks', fontsize=16, pad=20)
ax1.set_xlabel('Total Estimated Revenue ($ Billions)', fontsize=12)
ax1.set_ylabel('Median Approval Ratio', fontsize=12)

dev_patches = [
    mpatches.Patch(color=dev_colors[i], label=top_20.loc[i, 'developer'])
    for i in range(num_devs)
]
line_handles, _ = ax1.get_legend_handles_labels()

ax1.legend(
    handles=dev_patches + line_handles,
    loc='upper left',
    bbox_to_anchor=(1.01, 1),
    borderaxespad=0,
    fontsize=8,
    title="Developer",
    title_fontsize=9,
    framealpha=0.9
)

# --- Graph 2: Revenue Ranking with Approval Heatmap ---
sns.barplot(
    data=top_20,
    x=top_20['total_revenue'] / 1e6,
    y='developer',
    hue='median_approval',
    palette='viridis',
    ax=ax2,
    dodge=False
)

if ax2.get_legend():
    ax2.get_legend().remove()

ax2.set_title('Top 20 Developers by Total Revenue', fontsize=16, pad=20)
ax2.set_xlabel('Revenue ($ Millions)', fontsize=12)
ax2.set_ylabel('Developer', fontsize=12)

sm = plt.cm.ScalarMappable(
    cmap="viridis",
    norm=mcolors.Normalize(vmin=top_20['median_approval'].min(), vmax=top_20['median_approval'].max())
)
fig.colorbar(sm, ax=ax2, location='right', shrink=0.8, pad=0.02, label='Approval Ratio')

plt.tight_layout(rect=(0, 0, 0.78, 1))

graph_path = Path(save_file_path / "q5_top_20_developer_efficiency.png")
plt.savefig(graph_path, bbox_inches='tight')
plt.show()

print(f"Analysis complete. Graph saved to: {graph_path}")



# Global Metrics
# global mean = 0.8077336436177566, median=0.8439878234398782, approval rating

#--- Top 20 Developers by Revenue Efficiency (Ranked by Total Revenue + Approval Ratio) ---
#     developer                  total_games  total_owners  median_owners  total_revenue          mean_revenue         median_revenue       std_dev_revenue      mean_approval  median_approval  std_dev_approval  rank_score
# 0   Valve                      18           189000000.0   7500000.0      1207110000.0(1207.11M) 67061666.6(67.06M)   53925000.0(53.92M)   34899058.1(34.89M)   0.897590       0.944236         0.116837          1.545874
# 1   Feral Interactive (Mac)    39           65525000.0    1500000.0      1304689750.0(1304.68M) 33453583.3(33.45M)   29970000.0(29.97M)   30772222.6(30.77M)   0.825986       0.855804         0.118453          1.490440
# 2   Aspyr                      21           55100000.0    1500000.0      1157699000.0(1157.69M) 55128523.8(55.12M)   25165000.0(25.16M)   56399205.0(56.39M)   0.801821       0.879170         0.151375          1.445208
# 3   PUBG Corporation           1            75000000.0    75000000.0     2024250000.0(2024.25M) 2024250000.0(2024.25M)2024250000.0(2024.25M)0.0(0.00M)           0.504631       0.504631         0.000000          1.434353
# 4   Aspyr (Mac)                16           48100000.0    1500000.0      1081819000.0(1081.81M) 67613687.5(67.61M)   48735000.0(48.73M)   59201150.9(59.20M)   0.814452       0.890679         0.154346          1.421211
# 5   Feral Interactive (Linux)  19           40600000.0    1500000.0      960844000.0(960.84M)   50570736.8(50.57M)   52465000.0(52.46M)   36477814.9(36.47M)   0.792536       0.831280         0.147515          1.291835
# 6   Ubisoft                    53           44535000.0    350000.0       932635650.0(932.63M)   17596899.0(17.59M)   6442500.0(6.44M)     24265930.4(24.26M)   0.761411       0.782788         0.138725          1.221067
# 7   CAPCOM Co., Ltd.           12           14775000.0    750000.0       574577250.0(574.57M)   47881437.5(47.88M)   8794500.0(8.79M)     105682685.6(105.68M) 0.834892       0.878730         0.116446          1.156622
# 8   CAPCOM                     15           15425000.0    350000.0       584770750.0(584.77M)   38984716.6(38.98M)   5596500.0(5.59M)     95473222.3(95.47M)   0.788812       0.852240         0.181371          1.130613
# 9   Firaxis Games              11           26250000.0    1500000.0      521237500.0(521.23M)   47385227.2(47.38M)   14985000.0(14.98M)   60321072.5(60.32M)   0.812524       0.864230         0.148255          1.113279
# 10  Ubisoft Montreal           20           30100000.0    1125000.0      574024000.0(574.02M)   28701200.0(28.70M)   12885000.0(12.88M)   33270111.7(33.27M)   0.807704       0.836085         0.093066          1.106371
# 11  Relic                      11           25000000.0    1500000.0      342250000.0(342.25M)   31113636.3(31.11M)   22492500.0(22.49M)   19844369.7(19.84M)   0.859839       0.909342         0.149461          1.077725
# 12  FromSoftware               4            10000000.0    2500000.0      404585000.0(404.58M)   101146250.0(101.14M) 92475000.0(92.47M)   66377377.2(66.37M)   0.883135       0.882258         0.021545          1.076779
# 13  Aspyr (Linux)              5            23500000.0    3500000.0      624765000.0(624.76M)   124953000.0(124.95M) 149925000.0(149.92M) 51339075.9(51.33M)   0.775083       0.769115         0.175215          1.052951
# 14  Infinity Ward              6            11950000.0    1125000.0      280380500.0(280.38M)   46730083.3(46.73M)   29988750.0(29.98M)   54455860.1(54.45M)   0.779238       0.912768         0.219687          1.051175
# 15  Relic Entertainment        10           21500000.0    1500000.0      272285000.0(272.28M)   27228500.0(27.22M)   22488750.0(22.48M)   15908134.8(15.90M)   0.855025       0.913467         0.156644          1.047995
# 16  Gearbox Software           10           28775000.0    1125000.0      364272250.0(364.27M)   36427225.0(36.42M)   21363750.0(21.36M)   50496935.4(50.49M)   0.829515       0.864289         0.106459          1.035803
# 17  Bethesda Game Studios      9            33550000.0    1500000.0      514164500.0(514.16M)   57129388.8(57.12M)   19485000.0(19.48M)   61437016.9(61.43M)   0.824400       0.797859         0.099262          1.031999
# 18  Facepunch Studios          2            22500000.0    11250000.0     313275000.0(313.27M)   156637500.0(156.63M) 156637500.0(156.63M) 73238584.8(73.23M)   0.880405       0.880405         0.107999          1.029498
# 19  Treyarch                   4            10000000.0    2500000.0      342400000.0(342.40M)   85600000.0(85.60M)   86225000.0(86.22M)   47440270.8(47.44M)   0.818106       0.866276         0.142620          1.027327



# Observation
# 1. Macro Analysis (Product Quality vs. Commercial Viability):
# On a surface level, the top 20 developers demonstrate a strong equilibrium between critical 
# success and commercial execution. All studios hover near or above the global baseline metrics 
# (mean: ~80.8%, median: ~84.4%), confirming that high revenue generation in this tier is 
# generally coupled with strong, baseline product delivery.
#
# 2. Portfolio Strategies: Specialized Focus vs. Corporate Scaling
# The dataset exposes two distinct operational philosophies within the top 20:
#   A. High-Efficiency Snipers (< 5 Games): Studios like FromSoftware (4 games) display 
#      immense financial and critical efficiency. With an exceptional median revenue (~$92.5M) 
#      and owner count (2.5M), their portfolio represents a concentrated collection of cultural 
#      milestones where every product secures premium market capture and high player loyalty.
#
#   B. High-Volume Ecosystems (> 5 Games): Larger publishers like Ubisoft (53 games) show a 
#      "long-tail" distribution. While total revenue remains high due to portfolio scale, their 
#      median approval ratings and median revenues ($6.4M) are significantly lower than their 
#      low-volume peers. This indicates a business model reliant on steady, programmatic 
#      monetization across a vast library, rather than uniform critical acclaim.
#
# 3. Institutional Outliers: Valve & PUBG Corporation
#   * Valve: Dominates with the highest median approval rating (94.4%). This reflects a structural 
#     "home-ground" platform advantage combined with a historical catalog of high-retention, cult 
#     classics. Valve prioritizes long-term product lifespans over high release frequency.
#   * PUBG Corporation: Represents a pure genre-defining outlier. It achieves the highest 
#     individual game revenue ($2.02B) off a single title by commercializing the Battle Royale 
#     genre. However, it holds the lowest approval rating in the top 20 (~50.5%), highlighting a 
#     common live-service trajectory where massive commercial monetization persists despite severe 
#     player sentiment decay over time.
#
# 4. Temporal Constraints and Market Realities (2019 Snapshot vs. 2026 Context):
# It is vital to note that this dataset heavily reflects historical market standings up to 2019. 
# In the current 2026 landscape, public sentiment and brand equity for several major publishers 
# listed here—most notably Ubisoft and Bethesda—have undergone severe decline due to recent 
# release controversies and changing live-service expectations. If real-time 2026 data were 
# introduced, the ranking distribution would shift dramatically for corporate publishers, while 
# legacy anchors like Valve and high-reputation studios like FromSoftware would maintain dominance.
#
# 5. Sentiment Skewness (Median vs. Mean Divergence):
# Across the top tier, we observe a negative skew where the Approval Median consistently exceeds 
# the Mean. From an industry perspective, this divergence indicates that while a studio's core 
# catalog maintains tight, reliable quality standards (reflected in a high median), the overall 
# average is heavily dragged down by severe, isolated negative outliers. This is the mathematical 
# signature of modern platform volatility—such as "review-bombing" campaigns, retroactive backlash 
# against post-launch monetization updates, or high-profile "hate-play" titles within an otherwise 
# respected corporate catalog.
#
# Summary Conclusion:
# Premium ranking is achieved either through specialized critical excellence that guarantees high 
# per-unit revenue (FromSoftware), massive historical platform advantage (Valve), structural genre 
# monopoly (PUBG), or high-volume porting and catalog scaling (Feral/Aspyr/Ubisoft).





# Observation: my workd without any structure.
# From the data i can say all top 20 games interm of revenue and approval rating
# (on surface level) all the top game re doing generally good job and earning profit at the same time giving
# good product delivery since the all develop are nearly around same global mean and median.
# but say looking at median approval rating, the develop like valve do have a big advantage since steam
# is their home ground, so i dont this steam being at the top is not something that is unheard of, since
# valve do publish games but the count if value is generally low amount of games but almost like 90% of their
# games are cult classic like l4d,l4d2, hl2 and so on.
# about other developer with games <5 this mean those dev are doing really great work at delivering their games
# and capturing majortity of player and earning the revenue, if i am being clear i have never heard of most of the
#  developer but say i take the from software developer example
# all the 4 games here is garuntee (ds1,ds2,ds3 and elden ring). and these are very highly rated game and no one is going 
# to regret ever buying these games.
# the develop >5 games, they do are earning revenue but their on median approval is really low as compared to other in top 20
# and the standard dev is like some what consistant with other abit on few minor point on higher,
# so this say they are earning money from all games (since the median and std_dev revenue is low and consistant),
# but the gamers dont have high regard on the games.
# finally about Pubg Corp, dyam color me suprised earning like highest revenue with just 1 game,
# i do say this is not suprising since they popularized a whole new genre called battle royale,
# while their revenue is really high but the approval rating is lowest at ~55% due to fact that 
# PUBG is getting old and it is really not that popular these days and fortknight  is having all craze from battale royale
# so Finallt i can say most top company are earning revenue and they are also delivering cult classic games, while 
# have high rating.
# but finally there is still 1 issue need to be addressed since the data is from 2019 and current is 2026,
# these days people are really angry on Ubisoft and Bethesda , if the actual data from current year available this ranking 
# cart will be 99% different but the valve will be still dominating the chart
#	In this special instance the median > mean this means that on average gamers give
#	consistant rating but there are some cases like review bombing, or some special cases
#	where players change their orgginal review to negative review due to some change in game
# 	or some games just do hate play on games.