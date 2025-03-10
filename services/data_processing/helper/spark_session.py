from pyspark.sql import SparkSession


def get_spark_session():
    """Get a spark session"""
    spark = SparkSession.builder \
        .appName("AgeDataProcessing") \
        .getOrCreate()
        # .config("spark.jars", "/Downloads/spark-excel_2.12-0.13.5.jar") \
    return spark
