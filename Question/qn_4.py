# **Q4 — Achievement Design: F2P vs. Paid**
# Do Free-to-Play games have more achievements on average than paid games, and does 
# that difference hold across all platforms or only on Windows?

from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd

base_path: Path = Path(__file__).resolve().parent.parent
path: Path = base_path / "data" / "cleaned_data.csv"
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