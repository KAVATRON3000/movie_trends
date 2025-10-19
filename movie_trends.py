import pandas as pd
import matplotlib.pyplot as plt

try: # Load the dataset from the data folder
    df = pd.read_csv('data/movies_metadata.csv', low_memory=False)
    print("File loaded successfully.")
    print(f"Shape of the dataset (rows, columns): {df.shape}")
except FileNotFoundError:
    print(f'Error: The file was not found.')
    print("Please make sure the movies_metadata.csv file is in the data folder.")

if df is not None: # Only if the file is loaded, get a quick feel of the data
    print(df.head())
    df.info()