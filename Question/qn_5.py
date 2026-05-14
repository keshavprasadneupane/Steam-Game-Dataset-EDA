from pathlib import Path
from typing import Any
import pandas as pd

# --- Data Loading ---
current_file = Path(__file__).resolve()
base_path: Path = current_file.parent.parent
path: Path = base_path / "data" / "cleaned_data.csv"
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

print("\n--- Top 10 Developers by Revenue Efficiency (Ranked by Total Revenue + Approval Ratio) ---")
print(sorted_df.head(10))

output_path = Path(current_file.parent / "qn_5_output.csv")
sorted_df.to_csv(output_path, index=False)


import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from pathlib import Path

# --- Visualization for Top 20 ---

# 1. Clean the data: Remove non-ASCII characters to prevent font errors
# and take the Top 20
top_20 = sorted_df.head(20).copy()
top_20['developer'] = top_20['developer'].apply(
    lambda x: ''.join([i if ord(i) < 128 else '' for i in x]).strip()
)

# Set visual style
plt.style.use('ggplot')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 18))

# --- Graph 1: Revenue vs Approval Ratio (Efficiency) ---
scatter = ax1.scatter(
    top_20['total_revenue'] / 1e9,
    top_20['median_approval'],
    s=top_20['total_games'] * 80,  # Size by game count
    c=top_20['median_approval'],
    cmap='RdYlGn',
    alpha=0.7,
    edgecolors="black"
)

# Global Benchmarks (Horizontal Lines)
ax1.axhline(global_average, color='blue', linestyle='--', alpha=0.6, label=f'Global Mean ({global_average:.2f})')
ax1.axhline(global_median, color='purple', linestyle='-.', alpha=0.6, label=f'Global Median ({global_median:.2f})')

# Annotate developer names
for i, txt in enumerate(top_20['developer']):
    ax1.annotate(txt, (top_20['total_revenue'][i] / 1e9, top_20['median_approval'][i]),
                 fontsize=9, xytext=(5, 5), textcoords='offset points')

ax1.set_title('Top 20 Developer Efficiency vs. Global Benchmarks', fontsize=16, pad=20)
ax1.set_xlabel('Total Estimated Revenue ($ Billions)', fontsize=12)
ax1.set_ylabel('Median Approval Ratio', fontsize=12)
ax1.legend(loc='upper left')

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

# Remove automatic legend to use a proper colorbar
if ax2.get_legend():
    ax2.get_legend().remove()

ax2.set_title('Top 20 Developers by Total Revenue', fontsize=16, pad=20)
ax2.set_xlabel('Revenue ($ Millions)', fontsize=12)
ax2.set_ylabel('Developer', fontsize=12)

# Colorbar for Approval Ratio
sm = plt.cm.ScalarMappable(
    cmap="viridis", 
    norm=mcolors.Normalize(vmin=top_20['median_approval'].min(), vmax=top_20['median_approval'].max())
)
# Fixed: Pass the tuple (left, bottom, width, height)
cbar_ax = fig.add_axes((0.92, 0.15, 0.02, 0.7)) 
fig.colorbar(sm, cax=cbar_ax, label='Approval Ratio')

plt.tight_layout(rect=(0, 0, 0.9, 1)) # Adjust layout to fit colorbar

# Save and Show
graph_path = Path(current_file.parent / "top_20_developer_efficiency.png")
plt.savefig(graph_path)
plt.show()

print(f"Analysis complete. Graph saved to: {graph_path}")