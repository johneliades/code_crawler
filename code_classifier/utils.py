import sqlite3
import pandas as pd
import pickle
import pynvml 

def print_gpu_utilization():
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU memory occupied: {info.used//1024**2} MB.")

def sql_to_pkl(database):
    # Create a SQL connection to our SQLite database
    conn = sqlite3.connect(database)

    # Get a list of all tables in the database
    cursor = conn.cursor()
    tables = cursor.execute("SELECT name from sqlite_master WHERE type='table';").fetchall()

    df = pd.read_sql_query(f"SELECT snippet, language from snippets WHERE language != 'UNKNOWN'", conn)

    x = df['snippet']
    y = df['language']

    #print(df['language'].unique())
    df['language'].replace(df['language'].unique(), list(range(len(df['language'].unique()))), inplace=True)

    # Close the connection
    conn.close()

    # Saving the dataframe
    with open('./code_snippet/snippets-dev.pkl', 'wb') as file:
        pickle.dump(df, file)

def load_pkl(dataframe):
    # Loading the dataframe
    with open(dataframe, 'rb') as file:
        df = pickle.load(file)
        
    return df