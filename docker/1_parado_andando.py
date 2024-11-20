import os
import sys
import pandas as pd

# TODO: Improve imports, use absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from preprocess.movement import stopped_df

file_name = os.path.basename(__file__)

def log_message(message):
    print(f"[{file_name}]: {message}")

def log_error(message):
    print(f"[{file_name} - ERROR]: {message}")

if __name__ == '__main__':
    path = './'

    if not os.path.exists("parado/"): os.makedirs("parado/")

    file_path = path + "dados/nox.csv"
    if os.path.exists(file_path):
        log_message(f"File {file_path} exists, generating DataFrame")
        df = pd.read_csv(path + "dados/nox.csv", index_col=[0])
        df = stopped_df(df)
        csv_path = path + "parado/nox.csv"
        df.to_csv(csv_path)
        log_message(f"DataFrame saved to {csv_path}")
        print(df)
    else:
        log_error(f"File {file_path} not found")
