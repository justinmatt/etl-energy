import logging
import os
import sys
from src.etls.bronze.load_json import LoadedJSON, load_json_data
from src.etls.utils.schema import bronze_schema
from src.etls.utils.spark import get_spark, build_spark_table, write_to_postgres
from src.etls.silver.bronze2silver import TransformationPowerData
from src.etls.gold.silver2gold import TransformationPowerDataGold
# Add the project root to the python path to ensure imports work correctly
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.etls.collectors.api_collect import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BRONZE_PATH = "./data_storage/bronze/"
BRONZE_PATH_META = "./data_storage/bronze/meta_data"
spark = get_spark()

def Api2Bronze(api_url: str):
    """
    Main entry point for the ETL process.
    """
    logging.info("Starting ETL Energy Data Collection...")
    

    # Run the collection
    client = APIClient(timeout=30, max_attempts=3)

    result = client.fetch(api_url=api_url)
    #save requested data and meta data
    client._save_json(data=result['req_data'], path=result['data_path'])
    client._save_json(data=result['metadata'], path=result['meta_path'])


    if result['status']=='success':
        logging.info(f"ETL Job Completed. Data available at: {result['data_path']}")
        logging.info(f"Meta data available at {result['meta_path']}")
    else:
        logging.error(f"ETL Job status {result['status']}. No api data saved.")
        logging.info(f"Meta data available at {result['meta_path']}")




if __name__ == "__main__":

    api_url = "https://api.energy-charts.info/price?bzn=DE-LU" 
    table_name = 'energy_price_silver'

    Api2Bronze(api_url=api_url)

    json_load = load_json_data(bronze_path=BRONZE_PATH, meta_path=BRONZE_PATH_META)
    json_data = json_load.json_data | json_load.meta_data

    silver_df = TransformationPowerData(json_data=json_data, schema=bronze_schema, spark=spark)

    write_to_postgres(df=silver_df, table_name='energy_price_silver')


    gold_df = TransformationPowerDataGold(table=table_name, spark=spark)

    write_to_postgres(df=gold_df, table_name='energy_price_gold')