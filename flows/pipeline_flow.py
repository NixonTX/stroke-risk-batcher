import subprocess
from prefect import flow, task
import logging

# Configure logging
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define tasks with retries and logging
@task(retries=3, retry_delay_seconds=60)
def run_fetch_fitbit_data():
    logging.info("Starting fetch_fitbit_data.py")
    try:
        result = subprocess.run(
            ["python", "scripts/fetch_fitbit_data.py"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("fetch_fitbit_data.py completed successfully")
        logging.info(f"fetch_fitbit_data.py output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"fetch_fitbit_data.py failed: {e.stderr}")
        raise

@task(retries=3, retry_delay_seconds=60)
def run_train_model_db():
    logging.info("Starting train_model_db.py")
    try:
        result = subprocess.run(
            ["python", "scripts/train_model_db.py"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("train_model_db.py completed successfully")
        logging.info(f"train_model_db.py output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"train_model_db.py failed: {e.stderr}")
        raise

@task(retries=3, retry_delay_seconds=60)
def run_refresh_fitbit_token():
    logging.info("Starting refresh_fitbit_token.py")
    try:
        result = subprocess.run(
            ["python", "scripts/refresh_fitbit_token.py"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("refresh_fitbit_token.py completed successfully")
        logging.info(f"refresh_fitbit_token.py output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"refresh_fitbit_token.py failed: {e.stderr}")
        raise

# Define the main flow for data fetching and model training
@flow(name="stroke-risk-pipeline")
def stroke_risk_pipeline():
    fetch_data = run_fetch_fitbit_data()
    run_train_model_db(depends_on=fetch_data)

# Define the flow for token refresh
@flow(name="token-refresh-pipeline")
def token_refresh_pipeline():
    run_refresh_fitbit_token()

if __name__ == "__main__":
    # Run the flows manually for testing
    stroke_risk_pipeline()
    token_refresh_pipeline()