import os
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def download_dataset(output_dir: str):
    """
    Downloads the PaySim dataset (ealaxi/paysim1) from Kaggle.
    Requires kaggle.json API token configured in ~/.kaggle/ or KAGGLE_CONFIG_DIR.
    """
    logger.info(f"Preparing to download ealaxi/paysim1 to {output_dir}...")
    
    # Check if Kaggle token exists (either in environment or home folder)
    home = os.path.expanduser("~")
    kaggle_path = os.path.join(home, ".kaggle", "kaggle.json")
    env_kaggle_json = os.environ.get("KAGGLE_CONFIG_DIR")
    
    if not os.path.exists(kaggle_path) and not env_kaggle_json:
        logger.warning(
            "Kaggle API credentials not found. To download the dataset:\n"
            "1. Register on Kaggle and download kaggle.json from 'Your Profile' -> 'Account' -> 'Create New API Token'.\n"
            "2. Place kaggle.json in ~/.kaggle/ or set KAGGLE_CONFIG_DIR environment variable.\n"
            "Proceeding with placeholder/graceful exit."
        )
        return False
        
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        logger.info("Kaggle API authenticated successfully. Initiating download...")
        
        os.makedirs(output_dir, exist_ok=True)
        # Download and unzip
        api.dataset_download_files("ealaxi/paysim1", path=output_dir, unzip=True)
        logger.info(f"Dataset downloaded and extracted successfully to {output_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to download dataset from Kaggle: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download PaySim dataset from Kaggle")
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="data/raw/paysim", 
        help="Target directory to save the downloaded dataset"
    )
    args = parser.parse_args()
    
    download_dataset(args.output_dir)
