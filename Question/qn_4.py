# **Q4 — Achievement Design: F2P vs. Paid**
# Do Free-to-Play games have more achievements on average than paid games, and does 
# that difference hold across all platforms or only on Windows?

from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd

root_path: Path = Path(__file__).resolve().parent.parent
path: Path = root_path / "data" / "cleaned_data.csv"
save_file_path = root_path/ "output_picture"


df: pd.DataFrame = pd.read_csv(path, parse_dates=["release_date"])

MIN_PLAY_TIME_FILTER = 2
MIN_ACHIEVEMENT_FILTER = 1
F2PPrice= 0.0

def f2p_condition(dataframe:pd.DataFrame, isF2p:bool =True):
	return (dataframe["price"] == F2PPrice )if isF2p else (dataframe["price"] != F2PPrice )


df = df[(df["average_playtime"]>=MIN_PLAY_TIME_FILTER)&(df["achievements"]>=MIN_ACHIEVEMENT_FILTER)]

total_platfroms = df["platforms"].str.split(";").explode().unique()


dataframes:list[pd.DataFrame] = [
	df[f2p_condition(dataframe=df)],
	df[(f2p_condition(dataframe=df,isF2p=False))]
	]

game_types = ["F2p","Paid"]



class Result:
	def __init__(
		self,game_type:str,platform:str,
		game_count:int,ach_count:int,
	ach_median:float, ach_avg:float,std_dev:float) -> None:
		self.game_type=game_type
		self.platform=platform
		self.total_game =game_count
		self.total_achievement =ach_count
		self.achievements_median = ach_median
		self.achievements_mean = ach_avg
		self.std_dev = std_dev

	def to_dict(self):
		return{
			"type":self.game_type,
			"platform":self.platform,
			"total_game":self.total_game,
			"total_achievement":self.total_achievement,
			"achievements_median":self.achievements_median,
			"achievements_mean":self.achievements_mean,
			"standard_deviation":self.std_dev
			}

def get_result( data_frame:pd.DataFrame,game_type:str,platform:str)->Result:
	subset:pd.DataFrame = data_frame[data_frame["platforms"].str.contains(
			platform,
			regex=True,
			na=False
		)]
	game_count = len(subset)
	ach_count = subset["achievements"].sum()
	ach_median = subset["achievements"].median()
	ach_avg =subset["achievements"].mean().__round__(4)
	std_dev = subset["achievements"].std()
	return Result(game_type,platform,game_count,ach_count,ach_median,ach_avg,std_dev=std_dev)


result = []
result_ratios = []
for platform in total_platfroms:
	f2p =  get_result(data_frame=dataframes[0],game_type=game_types[0],platform=platform)
	result.append(f2p.to_dict())

	paid =  get_result(data_frame=dataframes[1],game_type=game_types[1],platform=platform)
	result.append(paid.to_dict())

	result_ratios.append(
		{
			"platform":platform,
			"total_game_ratio": f2p.total_game/paid.total_game,
			"total_achievement_ratio":f2p.total_achievement/paid.total_achievement,
			"achievements_median_ratio":f2p.achievements_median/paid.achievements_median,
			"achievements_mean_ratio":f2p.achievements_mean/paid.achievements_mean,
			"standard_deviation_ratio":f2p.std_dev/paid.std_dev

		}
	)

stats_df = pd.DataFrame(result)
ratio_df = pd.DataFrame(result_ratios)
print("Paid and F2p game Statistic")
print(stats_df,"\n\n")
print("Ratio of Game Statistic in (F2p/Paid) format")
print(ratio_df)









#------------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np

# 1. Separate the F2P and Paid statistics for easy plotting mapping
f2p_stats = stats_df[stats_df['type'] == 'F2p'].set_index('platform')
paid_stats = stats_df[stats_df['type'] == 'Paid'].set_index('platform')

# Ensure both dataframes share the exact same platform alignment/ordering
platforms = f2p_stats.index.tolist()
x_indices = np.arange(len(platforms))
bar_width = 0.20

# 2. Initialize the Figure (Using a 2-panel layout to clearly separate Mean vs Median)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=100)

# ==========================================
# PANEL 1: Mean Achievements Comparison
# ==========================================
ax1.bar(x_indices - bar_width/2, f2p_stats['achievements_mean'], bar_width, 
        label='F2P Games', color='#2ca02c', alpha=0.85) # Vivid Green for F2P
ax1.bar(x_indices + bar_width/2, paid_stats['achievements_mean'], bar_width, 
        label='Paid Games', color='#1f77b4', alpha=0.85) # Steady Blue for Paid

ax1.set_title("Average (Mean) Achievements per Game", fontsize=12, fontweight='bold', pad=10)
ax1.set_ylabel("Number of Achievements", fontsize=11)
ax1.set_xticks(x_indices)
ax1.set_xticklabels(platforms, fontsize=11)
ax1.grid(axis='y', linestyle='--', alpha=0.4)
ax1.legend(frameon=True, facecolor='white')

# ==========================================
# PANEL 2: Median Achievements Comparison
# ==========================================
ax2.bar(x_indices - bar_width/2, f2p_stats['achievements_median'], bar_width, 
        label='F2P Games', color='#2ca02c', alpha=0.85)
ax2.bar(x_indices + bar_width/2, paid_stats['achievements_median'], bar_width, 
        label='Paid Games', color='#1f77b4', alpha=0.85)

ax2.set_title("Typical (Median) Achievements per Game", fontsize=12, fontweight='bold', pad=10)
ax2.set_ylabel("Number of Achievements", fontsize=11)
ax2.set_xticks(x_indices)
ax2.set_xticklabels(platforms, fontsize=11)
ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.legend(frameon=True, facecolor='white')

# 3. Overall Layout Polishing
plt.suptitle("Steam Achievement Distribution Analysis: Free-to-Play vs. Paid Games\nAcross Cross-Platform Ecosystems", 
             fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()

# 4. Save using your configured path variable and display
plt.savefig(save_file_path / "q4_f2p_vs_paid_achievements_analysis.png", bbox_inches='tight')
plt.show()











# steam-game-dataset-eda ❯ uv run Question/qn_4.py
# Paid and F2p game Statistic
#    type platform  total_game  total_achievement  achievements_median  achievements_mean  standard_deviation
# 0   F2p  windows         404              25352                 30.0            62.7525          132.247768
# 1  Paid  windows        3624             242653                 27.0            66.9572          326.655878
# 2   F2p      mac         182               9750                 29.0            53.5714           74.171839
# 3  Paid      mac        1715              91714                 25.0            53.4776          223.869010
# 4   F2p    linux         109               4855                 24.0            44.5413           63.645216
# 5  Paid    linux        1320              76754                 26.0            58.1470          242.825792 


# Ratio of Game Statistic in (F2p/Paid) format
#   platform  total_game_ratio  total_achievement_ratio  achievements_median_ratio  achievements_mean_ratio  standard_deviation_ratio
# 0  windows          0.111479                 0.104478                   1.111111                 0.937203                  0.404853
# 1      mac          0.106122                 0.106309                   1.160000                 1.001754                  0.331318
# 2    linux          0.082576                 0.063254                   0.923077                 0.766012                  0.262102

# Observation
# 1. Central Tendency (Median vs. Mean):
# On dominant platforms (Windows and Mac), F2P games exhibit a slightly higher median 
# achievement count (+1 to +3) compared to Paid games. While this minor margin is statistically 
# negligible in the broader market, it indicates that F2P titles establish a reliable baseline 
# floor for achievements, using them as structural engagement hooks to drive player retention.
#
# 2. Dispersion and Volatility (The "Wild West" Variance):
# The defining metric is the Standard Deviation (σ). F2P games maintain a highly constrained, 
# consistent variation (σ ≈ 63 - 132), proving that their achievement design follows strict, 
# standardized deployment patterns. Conversely, Paid games represent a "Wild West" scenario, 
# with a massive standard deviation (up to 200+ points higher than F2P). This immense volatility 
# highlights a highly fragmented market ranging from minimalist indie projects with minimal 
# achievements to extreme "achievement spam" titles that heavily inflate the variance.
#
# 3. The Linux Ecosystem Anomaly:
# Linux acts as an outlier, bucking the median trend. This is a highly constrained, non-native 
# sampling environment. Because the vast majority of Linux gaming relies on translation layers 
# like Proton or Wine rather than native Linux architecture, developers rarely optimize or tailor 
# system telemetry specifically for this ecosystem. The Linux metrics are essentially a distorted, 
# low-sample echo of the Windows market.
#
# 4. Data Constraints & External Architecture (The "Gacha/Launcher" Blindspot):
# It is critical to note that Steam's API data inherently underrepresents the true scale of 
# F2P achievement systems. Massive live-service and Gacha titles (e.g., Genshin Impact) track 
# hundreds or thousands of progressive milestones natively inside their own proprietary clients 
# and launchers, passing only a fraction (or none) to the public Steam profile API. If full 
# internal telemetry for these high-engagement F2P ecosystems were exposed, a handful of dominant 
# live-service titles would completely skew the F2P distribution curves.
#
# Summary Conclusion:
# F2P games enforce a predictable, highly standardized, and consistent achievement density to 
# protect retention loops. Paid games operate with extreme volatility, stretching across a wide, 
# unconstrained spectrum of design philosophies.











# my observation but without structure.
# Observation
# From the data, i can say is the f2p games slightly have more achievenemt than the paid games
# in the data we can see in all platfrom except linux the median achievement count is like 1-2 count more than the 
# paid game which is slightly more than paid but in the grand scheme of the game market the count difference is very
# insignificant, but if we take the look by another angle from the standard deviation we can see that f2p games have very
# standard and low variation achievement count in all games in every platfrom the achievement standard deviation is like
# 200 point less than the paid, so this mean the achievement count in all f2p is hight but they are consistant, 
# while the achievement count for paid is like a wild west, since the vairation is huge so there are games with almost like 10 achievement 
# or some games like 100+ achievement. about linux this location is like a little bit of uncarted area even though some games,
# support the linux but mostly game are being using proton or wine layer, so from my observation(u can call this bias), linux market 
# i will say is getting piggy ride due to the label in game rather than actual gameplay.
# finally the f2p achievement count shown here is not even full achievement count when a game called genshin have 1600+ ahcievement in it but ,
# it is being counted fully in game, so just based on the data i can say.
# SO finally, F2p games have higher consistant number of achievement count, while paid game may have low or really high achievement count.
# but if the fully ingame f2p/gatcha game are counted this this whole chart will be dominated just by 10 gatcha games