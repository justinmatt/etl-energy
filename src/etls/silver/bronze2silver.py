# src/etl_energy/silver/bronze2silver.py

import logging
from typing import Any, Dict
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, slice, arrays_zip, explode, current_timestamp, lit, to_timestamp
from pyspark.sql.types import StructType
from src.etls.bronze.load_json import LoadedJSON, load_json_data
from src.etls.utils.schema import bronze_schema
from src.etls.utils.spark import get_spark, build_spark_table, write_to_postgres


BRONZE_PATH = "./data_storage/bronze/"
BRONZE_PATH_META = "./data_storage/bronze/meta_data"

spark = get_spark()

logger = logging.getLogger(__name__)

def TransformationPowerData(json_data: Dict, schema: StructType, spark: SparkSession = spark)->DataFrame:

    #  Convert raw python JSON → DataFrame 

    df = build_spark_table(spark, json_data, schema)

    # Convert array columns into one row per (price, unix_seconds) pair by zipping and exploding them.
    df_silver = (df
      .withColumn('rw_insert_time_key', to_timestamp(lit(current_timestamp())))
      .withColumn("zipped_col", arrays_zip("price", "unix_seconds"))
      .withColumn("exploded", explode("zipped_col"))
      .select(
          *[c for c in df.columns if c not in ("price", "unix_seconds")],
          col('exploded.price').alias('price'),
          col('exploded.unix_seconds').alias('unix_seconds')
      )
    )

    return df_silver




if __name__ == "__main__":
    json_load = load_json_data(bronze_path=BRONZE_PATH, meta_path=BRONZE_PATH_META)
    json_data = json_load.json_data | json_load.meta_data

    silver_df = TransformationPowerData(json_data=json_data, schema=bronze_schema, spark=spark)

    write_to_postgres(df=silver_df, table_name='energy_price_silver')