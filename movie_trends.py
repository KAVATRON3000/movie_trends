import numpy as np
import pandas as pd
from pandas import DataFrame
import ast
import matplotlib.pyplot as plt

def clean_movie_data(df: DataFrame) -> DataFrame:
    #print(df.head())
    #df.info()
    # Time to clean.
    print("Cleaning...")

    # Fix budget column, turning values from object to numeric. Bad values become NaN.
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
    # Since we can't analyse a movie with a budget of 0, replace with NaN.
    df['budget'] = df['budget'].replace(0, pd.NA)

    # Fix revenue column, converting to numeric and replacing with 0s.
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['revenue'] = df['revenue'].replace(0, pd.NA)

    # Fix release_date column, converting to datetime, coercing errors. Bad dates become NaT.
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

    # Drop rows with missing critical data.
    print(f'Shape before dropping missing values: {df.shape}')
    df.dropna(subset=['budget', 'revenue', 'release_date'], inplace=True)
    print(f'Shape after dropping missing values: {df.shape}')

    # This isn't data cleaning, but it will make data more readable when I plot my graphs.
    df['budget'] = df['budget'] / 1_000_000
    df['revenue'] = df['revenue'] / 1_000_000

    # Extract the release year into a new column.
    df['release_year'] = df['release_date'].dt.year

    # Finally, drop all columns that will not be analysed.
    columns_to_drop = [
        'adult', 'belongs_to_collection', 'homepage',
        'imdb_id', 'original_title', 'overview', 'poster_path',
        'production_companies', 'production_countries', 'spoken_languages',
        'status', 'tagline', 'video'
    ]
    df.drop(columns_to_drop, axis=1, inplace=True)

    #df.info()
    #print(df.head())

    # Interestingly, revenue, budget, and popularity are still an 'object' data type.
    # So, I will cast them as floats.

    df['budget'] = df['budget'].astype(float)
    df['revenue'] = df['revenue'].astype(float)
    df['popularity'] = df['popularity'].astype(float)

    # I will also cast vote_count as an int for good measure, can't have half a vote.
    df['vote_count'] = df['vote_count'].astype(int)

    # Not needed I just like how it looks when it prints the head.
    df = df.reset_index(drop=True)

    print("Data cleaned successfully.")
    df.info()
    print(df.head())

    return df

def load_data(data_path: str):
    try:  # Load the dataset from the data folder
        df = pd.read_csv(data_path, low_memory=False)
        print("File loaded successfully.")
        print(f"Shape of the dataset (rows, columns): {df.shape}")
        return df
    except FileNotFoundError:
        print("Error: The file was not found.")
        print("Please make sure the movies_metadata.csv file is in the data folder.")
        return None

def analyse_genres(df: DataFrame):
    # Finds the top 10 most common movie genres.
    # The genre column contains a serialised dict containing an id representing its genre,
    # and a human-readable string representing its genre.
    # Deserialises by SAFELY converting strings into a Python list.
    df['genres'] = df['genres'].apply(ast.literal_eval)
    # Extracts just the name from each dict in the list.
    genres_list = df['genres'].apply(lambda x: [i['name'] for i in x])
    # Transforms each item in a list into its own row.
    all_genres = genres_list.explode()
    genre_counts = all_genres.value_counts().head(10)

    # Plotting the graph
    plt.figure(figsize=(12,8))
    genre_counts.sort_values(ascending=True).plot(kind='barh', color='purple')
    plt.title("Top 10 Most Common Movie Genres")
    plt.xlabel('Number of Movies')
    plt.ylabel('Genre')
    plt.tight_layout()
    plt.savefig('visualisations/top_10_genres.png')
    print("Plot saved. [Top 10 Most Common Movie Genres]")

def analyse_budget_vs_revenue(df: DataFrame):
    # Movie Budget vs. Revenue
    # All this does is filter out any movies with a budget less than $1M,
    # as they could be inaccurate.
    df_filtered = df[df['budget'] > 1]

    plt.figure(figsize=(10,6))
    plt.scatter(df_filtered['budget'], df_filtered['revenue'], alpha=0.5, color='green')
    plt.title("Movie Budget vs. Revenue")
    plt.xlabel('Budget (in millions $)')
    plt.ylabel('Revenue (in millions $)')
    plt.grid(True)
    plt.savefig('visualisations/budget_vs_revenue_scatter.png')
    print("Plot saved. [Movie Budget vs. Revenue]")

def analyse_releases_over_time(df: DataFrame):
    # Releases Over Time
    yearly_counts = df['release_year'].value_counts().sort_index()
    # Filtering out very old years that have few movies to make the plot cleaner.
    yearly_counts = yearly_counts[yearly_counts.index > 1940]
    # The dataset ends in 2017, so I must account for that too.
    yearly_counts = yearly_counts[yearly_counts.index < 2017]

    plt.figure(figsize=(12, 6))
    yearly_counts.plot(kind='line', color='red')
    plt.title('Number of Movies Released Per Year (1941-2016)')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.grid(True)
    plt.savefig('visualisations/releases_over_time.png')
    print("Plot saved. [Movie Releases Over Time]")

def analyse_genre_profitability(df: DataFrame):
    # Genre Profitability
    # Calculates profit for each movie.
    df['profit'] = df['revenue'] - df['budget']
    # Ensures the genres column is in the correct list format.
    if isinstance(df['genres'].iloc[0], str):
        df['genres'] = df['genres'].apply(ast.literal_eval)
    # Extracts genre names into a list.
    df['genre_names'] = df['genres'].apply(lambda x: [i['name'] for i in x])
    # Explodes the DataFrame to have one row per genre per movie.
    df_exploded = df.explode('genre_names')
    # Groups by genre name and calculate mean profit,
    # also counting num of movies to ensure sample size is reasonable.
    genre_profit = df_exploded.groupby('genre_names')['profit'].agg(['mean', 'count'])
    # Filters out genres with a small number of movies for a more stable average.
    genre_profit = genre_profit[genre_profit['count'] > 50]
    # Sorts by the average profit.
    genre_profit = genre_profit.sort_values(by='mean', ascending=False).head(10)

    # Plotting time
    plt.figure(figsize=(12, 8))
    genre_profit['mean'].sort_values(ascending=True).plot(kind='barh', color='blue')
    plt.title('Top 10 Most Profitable Movie Genres (Average Profit)')
    plt.xlabel('Average Profit (in millions $)')
    plt.ylabel('Genre')
    plt.tight_layout()
    plt.savefig('visualisations/top_10_profitable_genres.png')
    print("Plot saved. [Movie Genres Profitability]")

if __name__ == '__main__':

    DATA_PATH = 'data/movies_metadata.csv'
    df = load_data(DATA_PATH)

    if df is not None:
        df_cleaned = clean_movie_data(df.copy())
        if df_cleaned is not None and not df_cleaned.empty:
            analyse_genres(df_cleaned.copy())
            analyse_budget_vs_revenue(df_cleaned.copy())
            analyse_releases_over_time(df_cleaned.copy())
            analyse_genre_profitability(df_cleaned.copy())
        else:
            print("Data cleaning resulted in an empty DataFrame.")
    else:
        print("Exiting script.")