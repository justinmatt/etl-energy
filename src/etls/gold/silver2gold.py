
import logging
from typing import Any, Dict
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, slice, arrays_zip, explode, current_timestamp, lit, to_timestamp, from_unixtime
from pyspark.sql.types import StructType
from src.etls.bronze.load_json import LoadedJSON, load_json_data
from src.etls.utils.schema import bronze_schema
from src.etls.utils.spark import get_spark, build_spark_table, write_to_postgres, read_from_postgres



spark = get_spark()

logger = logging.getLogger(__name__)

def TransformationPowerDataGold(table: str, spark: SparkSession = spark)->DataFrame:

    #  Load the silver table

    df = read_from_postgres(spark=spark, table_name=table)

    # Convert silver table into gold 

    df_gold = df.withColumn(
    "timePrice",
    from_unixtime(col("unix_seconds")).cast("timestamp")
    ).select(
        "req_time",
        "unit",
        "price",
        "timePrice"
    )

    return df_gold

