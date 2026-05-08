import pandas  as pd
sample_sizes = [100,500,1000,5000]
filter_play_time = 2

df = pd.read_csv("data/cleaned_data.csv")
filtered_df =  df[(df["average_playtime"]>filter_play_time) & (df["median_playtime"]>filter_play_time)]


csv_size = len(filtered_df)
print("csv_size = ",csv_size)
for i in sample_sizes:
	size = min(i-1,csv_size)
	df_:pd.DataFrame = filtered_df.sample(i-1,random_state=100)
	df_.to_csv(f"data/df_{i}.csv")

print(df.head())