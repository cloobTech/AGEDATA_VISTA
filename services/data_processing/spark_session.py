from pyspark.sql import SparkSession


def get_spark_session():
    """Get a spark session"""
    ad_spark = SparkSession.builder.appName("AgeDataProcessing").getOrCreate()
    return ad_spark


agd_spark = get_spark_session()

# Create a simple DataFrame
data = [("Alice", 34), ("Bob", 45), ("Cathy", 29)]
columns = ["Name", "Age"]
df = agd_spark.createDataFrame(data, columns)

# Show the DataFrame
df.show()

# Perform a basic operation: filter rows where age is greater than 30
filtered_df = df.filter(df.Age > 30)
filtered_df.show()

print(agd_spark)
