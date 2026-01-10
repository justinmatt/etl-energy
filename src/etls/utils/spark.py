
import logging
from typing import Any, Dict
import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

logger = logging.getLogger(__name__)

from pyspark.sql import SparkSession

def get_spark():
    return (SparkSession.builder
            .appName('etl_energy')
            .config("spark.jars", "/opt/jdbc/postgresql-42.6.0.jar")
            .getOrCreate())



def build_spark_table(
    spark: SparkSession,
    loaded_data: Dict,
    schema: StructType
) -> DataFrame:
    """
    Convert bronze JSON Python data into a Spark DataFrame.

    Parameters
    ----------
    spark : SparkSession
        Active Spark session.
    loaded_data : Dict
        Dict from a json file.
    schema : StructType
        Spark schema for validating incoming JSON shape.

    Returns
    -------
    DataFrame
        A clean DataFrame.
    """

    # -------- 1. Convert raw python Dict → DataFrame --------
    logger.info("Converting Python Dict to Spark DataFrame using provided schema.")

    try:
        spark = get_spark()
        df = spark.createDataFrame([loaded_data], schema=schema)
    except Exception as e:
        logger.error("Schema mismatch while loading Dict into Spark.", exc_info=True)
        raise

    return df



def write_to_postgres(df: DataFrame, table_name: str, mode: str = "append"):
    """
    Write a Spark DataFrame to a PostgreSQL table using JDBC.

    Args:
        df (DataFrame): Spark DataFrame to write.
        table_name (str): Target table name in Postgres.
        mode (str): Write mode: 'append', 'overwrite', 'ignore', 'error' (default 'append').
    """
    db_url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
    db_properties = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "driver": "org.postgresql.Driver"
    }

    df.write.jdbc(url=db_url, table=table_name, mode=mode, properties=db_properties)
    print(f"Data written to PostgreSQL table '{table_name}' successfully.")


def read_from_postgres(spark: SparkSession, table_name: str) -> DataFrame:
    """
    Read a PostgreSQL table into a Spark DataFrame using JDBC.

    Args:
        spark (SparkSession): Active Spark session.
        table_name (str): Table name to read from Postgres.

    Returns:
        DataFrame: Spark DataFrame containing the table data.
    """
    db_url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
    db_properties = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "driver": "org.postgresql.Driver"
    }

    df = spark.read.jdbc(url=db_url, table=table_name, properties=db_properties)
    print(f"Data read from PostgreSQL table '{table_name}' successfully.")
    return df