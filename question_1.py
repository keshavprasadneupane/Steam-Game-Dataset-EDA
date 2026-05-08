import pandas as pd

# me do this again layer, without any help from ai/inline suggestion.

print_count =30
# Set a minimum playtime threshold (in hours) for median calculation
# since if a game is not even played for 2 hours, it is unlikely to be a game
# that players are interested in, and including such games could 
# negatively skew the median playtime calculation.
min_playtime = 2

df: pd.DataFrame = pd.read_csv('data/data.csv')


df_primary_genre: pd.DataFrame = df.copy()


df_primary_genre["primary_genre"] = df_primary_genre["genres"].str.split(";").str[0]

print("Assuming the first genre listed is the primary genre,so this analysis focuses on the primary genre of each game.\n")
unique_genres = df_primary_genre["primary_genre"].unique()
print(f"Found {len(unique_genres)} unique primary genres:")
print(unique_genres, "\n\n")
print_count = min(print_count, len(unique_genres))


playtime_mean = df_primary_genre.groupby("primary_genre")["average_playtime"].mean().reset_index()
playtime_mean["average_playtime"] = playtime_mean["average_playtime"].round(2)
playtime_sorted = playtime_mean.sort_values(by="average_playtime", ascending=False).reset_index(drop=True)

print(f"--- Top {print_count} Genres by Highest Average (Mean) Playtime ---")
print(playtime_sorted.head(print_count), "\n\n")


mean_genre_counts = df_primary_genre["primary_genre"].value_counts().reset_index()
mean_genre_counts.columns = ['primary_genre', 'game_count']

print(f"--- Top {print_count} Genres by Game Count (Market Share) ---")
print(mean_genre_counts.head(print_count), "\n\n")




cleaned_df:pd.DataFrame = df_primary_genre[df_primary_genre["average_playtime"] >= min_playtime]
playtime_median = cleaned_df.groupby("primary_genre")["average_playtime"].median().reset_index()
playtime_median["average_playtime"] = playtime_median["average_playtime"].round(2)
playtime_median_sorted = playtime_median.sort_values(by="average_playtime", ascending=False).reset_index(drop=True)
print(f"--- Top {print_count} Genres by Highest Median Playtime (Min Playtime >= {min_playtime} hours) ---")
print(playtime_median_sorted.head(print_count))


median_genre_counts = cleaned_df["primary_genre"].value_counts().reset_index()
median_genre_counts.columns = ['primary_genre', 'game_count']
print(f"--- Top {print_count} Genres by Game Count (Market Share) with Median Playtime Filter (Min Playtime >= {min_playtime} hours) ---")
print(median_genre_counts.head(print_count))