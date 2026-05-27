import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_raw_data(file_path: str) -> pd.DataFrame:
    """
    Loads raw CSV data from the specified path.
    Falls back to the sample dataset if the requested path is not found.
    """
    if not os.path.exists(file_path):
        logger.warning(f"File not found at {file_path}. Falling back to sample dataset...")
        file_path = "data/sample/paysim_sample.csv"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Neither the specified path nor sample file '{file_path}' exists.")
            
    logger.info(f"Loading CSV data from {file_path}...")
    df = pd.read_csv(file_path)
    logger.info(f"Successfully loaded DataFrame with shape: {df.shape}")
    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load raw CSV dataset")
    parser.add_argument("--file_path", type=str, default="data/sample/paysim_sample.csv", help="Path to raw CSV file")
    args = parser.parse_args()
    
    df = load_raw_data(args.file_path)
    print(df.head(2))
