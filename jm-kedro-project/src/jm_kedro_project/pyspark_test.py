import os

# Explicitly set the Python executable for PySpark
os.environ["PYSPARK_DRIVER_PYTHON"] = "python"
os.environ["PYSPARK_PYTHON"] = "python"

from pyspark.sql import SparkSession

spark = SparkSession.builder.master('local[*]').appName('test').getOrCreate()
print(spark.version)
spark.stop()
