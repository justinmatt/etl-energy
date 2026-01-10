
from pyspark.sql.types import (
    StructType, StructField,
    BooleanType, StringType,
    ArrayType, DoubleType, LongType, TimestampType
)

bronze_schema =  StructType([
    StructField("deprecated", BooleanType(), True),
    StructField("license_info", StringType(), True),
    StructField("price", ArrayType(DoubleType(), containsNull=True), True),
    StructField("unit", StringType(), True),
    StructField("unix_seconds", ArrayType(LongType(), containsNull=True), True),
    StructField("req_time", StringType(), False),
    StructField("api_url", StringType(), False),
])

silver_schema = StructType([
    StructField("deprecated", BooleanType(), True),
    StructField("license_info", StringType(), True),
    StructField("unit", StringType(), True),
    StructField("price", DoubleType(), True),           # exploded price
    StructField("unix_seconds", LongType(), True),     # exploded timestamp
    StructField("req_time", StringType(), False),
    StructField("api_url", StringType(), False),
    StructField("rw_insert_time_key", TimestampType(), False),
])