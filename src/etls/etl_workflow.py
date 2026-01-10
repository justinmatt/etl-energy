import logging
import os
import sys
from src.etls.bronze.load_json import LoadedJSON, load_json_data
from src.etls.utils.schema import bronze_schema
from src.etls.utils.spark import get_spark, build_spark_table, write_to_postgres
# Add the project root to the python path to ensure imports work correctly
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.etls.collectors.api_collect import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def Api2Bronze(api_url: str):
    """
    Main entry point for the ETL process.
    """
    logging.info("Starting ETL Energy Data Collection...")
    

    # Run the collection
    client = APIClient(timeout=30, max_attempts=3)

    result = client.fetch(api_url=api_url)

    if result:
        logging.info(f"ETL Job Completed. Data available at: {result['data_path']}")
        logging.info(f"Meta data available at {result['meta_path']}")
    else:
        logging.error("ETL Job Failed. No data saved.")




if __name__ == "__main__":

    api_url = "https://api.energy-charts.info/price?bzn=DE-LU" 

    Api2Bronze(api_url=api_url)
