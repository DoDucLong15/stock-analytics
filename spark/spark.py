from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode, date_format, expr, element_at, to_timestamp, split
from pyspark.sql.types import StringType, StructType, StructField, IntegerType, ArrayType, TimestampType, DoubleType, DateType
import subprocess
import logging
import threading

def jobVN30Data(spark):
  json_schema = ArrayType(StructType([
    StructField("time", StringType(), True),
    StructField("open", IntegerType(), True),
    StructField("high", IntegerType(), True),
    StructField("low", IntegerType(), True),
    StructField("close", IntegerType(), True),
    StructField("volume", IntegerType(), True),
    StructField("ticker", StringType(), True),
    StructField("companyType", StringType(), True)
  ]))

    # Định nghĩa tham số Kafka
  # kafka_params = {
  #   "kafka.bootstrap.servers": "kafka:9092",
  #   "subscribe": "vn30",
  #   "startingOffsets": "latest",
  #   "failOnDataLoss": "false"
  # }

    # Đọc dữ liệu từ Kafka
  kafka_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "vn30") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

  print("Data vn30")
  kafka_df.printSchema()

    # Chuyển đổi cột 'value' từ dạng binary sang chuỗi JSON
  kafka_df = kafka_df.selectExpr("CAST(value AS STRING)")

  stock_df = kafka_df.select(from_json(col("value"), json_schema).alias("data"))

    # Sử dụng hàm explode để biến đổi mảng thành các hàng
  stock_df = stock_df.select(explode(col("data")).alias("stock_data")).select("stock_data.*")
  # Hiển thị schema của DataFrame kết quả
  stock_df.printSchema()

  query = stock_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()
  query.awaitTermination()
    # Định nghĩa đường dẫn xuất HDFS
  # output_path = "hdfs://namenode:8020/user/root/kafka_data"

  #   # Chỉ định vị trí checkpoint
  # checkpoint_location_hdfs = "hdfs://namenode:8020/user/root/checkpoints_hdfs"
  
  #   # Ghi dữ liệu vào HDFS dưới dạng file parquet
  # hdfs_query = stock_df.writeStream \
  #   .outputMode("append") \
  #   .format("json") \
  #   .option("path", output_path) \
  #   .option("checkpointLocation", checkpoint_location_hdfs) \
  #   .start()
    
  # hdfs_query.awaitTermination()

def jobStockRealtimeData(spark):
  json_schema = ArrayType(StructType([
    StructField("ticker", StringType(), True),
    StructField("time", StringType(), True),
    StructField("orderType", StringType(), True),
    StructField("investorType", StringType(), True),
    StructField("volume", IntegerType(), True),
    StructField("averagePrice", DoubleType(), True),
    StructField("orderCount", IntegerType(), True),
    StructField("prevPriceChange", DoubleType(), True),
    StructField("total_minutes", StringType(), True)
  ]))

    # Định nghĩa tham số Kafka
  kafka_params = {
    "kafka.bootstrap.servers": "kafka:9092",
    "subscribe": "stock_realtime4",
    "startingOffsets": "latest"
  }

    # Đọc dữ liệu từ Kafka
  kafka_df = spark.readStream.format("kafka").options(**kafka_params).load()
  
    # Chuyển đổi cột 'value' từ dạng binary sang chuỗi JSON
  kafka_df = kafka_df.selectExpr("CAST(value AS STRING)")

    # Chuyển đổi cột 'value' từ chuỗi JSON sang dữ liệu JSON
  data_df = kafka_df.select(from_json(col("value"), json_schema).alias("jsonData"))

  data_df = data_df.select(explode(col("jsonData")).alias("stock_data")).select("stock_data.*")

  print(data_df)
    # data_df = data_df.withColumn("jsonData.time", to_timestamp(element_at("jsonData.time", 1), "HH:mm:ss"))  # Điều chỉnh định dạng của chuỗi 'time' tương ứng

    # unique_data_df = data_df.select("jsonData.*").dropDuplicates(['total_minutes'])
  # query = data_df.writeStream.outputMode("append").format("console").start()

    
  # try:
  #   data_df.writeStream .format("org.elasticsearch.spark.sql") \
  #     .option("es.nodes", "https://big-data.es.asia-southeast1.gcp.elastic-cloud.com") \
  #     .option("es.port", "9243") \
  #     .option("es.resource", "data_realtime_28_12") \
  #     .option("es.net.http.auth.user", "elastic") \
  #     .option("es.net.http.auth.pass", "Fqlvu8CGw9jIGdxSsSSR4R1z") \
  #     .option("es.nodes.wan.only", "true") \
  #     .option("checkpointLocation", "../checkpoint") \
  #     .outputMode("append") \
  #     .start()
  #   logging.info("Dữ liệu đã được gửi thành công lên Elasticsearch!")
  # except Exception as e:
  #   logging.error("Đã xảy ra lỗi khi gửi dữ liệu lên Elasticsearch: %s", str(e))
  # query.awaitTermination() 

if __name__ == "__main__":
  # Khởi tạo SparkSession
  spark = SparkSession.builder.appName("KafkaToElasticsearch").getOrCreate()
  spark.sparkContext.setLogLevel("ERROR")

  t1 = threading.Thread(target=jobVN30Data, args=(spark,))
  t2 = threading.Thread(target=jobStockRealtimeData, args=(spark,))
  t1.start()
  t2.start()

  t1.join()
  t2.join()
