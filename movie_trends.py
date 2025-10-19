import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt

def clean_movie_data(df: DataFrame) -> DataFrame:
    print(df.head())
    df.info()
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
        print(f'Error: The file was not found.')
        print("Please make sure the movies_metadata.csv file is in the data folder.")
        return None

def analyse_genres(df):
    return

def analyse_budget_vs_revenue(df):
    return

def analyse_releases_over_time(df):
    return


if __name__ == '__main__':
    DATA_PATH = 'data/movies_metadata.csv'
    df = load_data(DATA_PATH)

    if df is not None:
        df_cleaned = clean_movie_data(df.copy())
        if df_cleaned is not None and not df_cleaned.empty:
            print("yep")
        else:
            print("Data cleaning resulted in an empty DataFrame.")
    else:
        print("Exiting script.")