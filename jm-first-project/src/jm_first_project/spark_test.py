from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("TestSpark") \
    .getOrCreate()

df = spark.range(5)
df.show()
