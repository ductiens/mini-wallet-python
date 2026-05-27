import sys
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PipelineOrchestrator")

def run_step(step_name: str, cmd: list):
    """Run a pipeline step as a subprocess and log outputs. Exit if failed."""
    logger.info(f"==================================================================")
    logger.info(f"STARTING STEP: {step_name}")
    logger.info(f"Command: {' '.join(cmd)}")
    logger.info(f"==================================================================")
    
    # Run using the current virtual environment python interpreter
    result = subprocess.run([sys.executable] + cmd, capture_output=False)
    
    if result.returncode != 0:
        logger.error(f"❌ STEP FAILED: {step_name} (Exit code: {result.returncode})")
        sys.exit(result.returncode)
        
    logger.info(f"✅ STEP SUCCESSFUL: {step_name}\n")

def run_all_pipelines():
    """Sequentially trigger each pipeline module to perform full data engineering & training cycle."""
    logger.info("Starting Fintech FraudOps Copilot Orchestrated Pipeline run...")
    
    # Define steps
    steps = [
        (
            "Data Profiling",
            ["-m", "pipelines.processing.profile_data", "--input_file", "data/sample/paysim_sample.csv"]
        ),
        (
            "Data Cleaning",
            ["-m", "pipelines.processing.clean_paysim", "--input_file", "data/sample/paysim_sample.csv"]
        ),
        (
            "Feature Engineering",
            ["-m", "pipelines.processing.feature_engineering", "--input_file", "data/processed/paysim_clean.csv"]
        ),
        (
            "Model Training",
            ["-m", "pipelines.training.train_model", "--features_file", "data/features/paysim_features.csv"]
        ),
        (
            "Model Evaluation",
            ["-m", "pipelines.training.evaluate_model"]
        ),
        (
            "Batch Inference Prediction",
            ["-m", "pipelines.inference.batch_predict", "--features_file", "data/features/paysim_features.csv"]
        ),
        (
            "Database Mongo Import",
            ["scripts/import_transactions_to_mongo.py"]
        )
    ]
    
    for name, cmd in steps:
        run_step(name, cmd)
        
    logger.info("🎉 CONGRATULATIONS! Entire Fintech FraudOps Pipeline completed successfully!")

if __name__ == "__main__":
    run_all_pipelines()
