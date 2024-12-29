from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round, first, last, min, max
import logging


def get_first_open(dataframe):
    first_open = dataframe.groupBy('ticker', 'company_type') \
        .agg(min('time').alias("first_time"), first('open').alias("first_open_value")) \
        .select('ticker', 'company_type', 'first_time', 'first_open_value')
    return first_open


def get_end_open(dataframe):
    end_open = dataframe.groupBy('ticker', 'company_type') \
        .agg(max('time').alias("end_time"), last('open').alias("end_open_value")) \
        .select('ticker', 'company_type', 'end_time', 'end_open_value')
    return end_open


def calculate_growth(dataframe):
    growth = dataframe.withColumn(
        "growth",
        round(((col("end_open_value") - col("first_open_value")) / col("first_open_value")) * 100, 2)
    )
    return growth


def calculate_metrics_per_ticker(dataframe):
    first_open = get_first_open(dataframe)
    end_open = get_end_open(dataframe)

    aggregated_data = dataframe.groupBy('ticker', 'company_type') \
        .agg(
            {'volume': 'sum', 'high': 'max', 'low': 'min'}
        ).withColumnRenamed("sum(volume)", "total_volume") \
         .withColumnRenamed("max(high)", "max_high") \
         .withColumnRenamed("min(low)", "min_low")

    aggregated_data = aggregated_data.join(first_open, on=['ticker', 'company_type'], how='inner')
    aggregated_data = aggregated_data.join(end_open, on=['ticker', 'company_type'], how='inner')
    aggregated_data = aggregated_data.withColumn(
        "price_range_percent",
        round(((col("max_high") - col("min_low")) / col("first_open_value")) * 100, 2)
    )
    aggregated_data = calculate_growth(aggregated_data)
    return aggregated_data


def save_to_cassandra(dataframe, keyspace, table):
    try:
        dataframe.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table=table, keyspace=keyspace) \
            .mode("append") \
            .save()
        logging.info(f"Dữ liệu đã được lưu vào Cassandra trong bảng {table}.")
    except Exception as e:
        logging.error(f"Lỗi khi lưu dữ liệu vào Cassandra: {str(e)}")


def save_to_elasticsearch(dataframe, es_resource, es_nodes="elasticsearch", es_port="9200"):
    try:
        dataframe.write.format("org.elasticsearch.spark.sql") \
            .option("es.nodes", es_nodes) \
            .option("es.port", es_port) \
            .option("es.resource", es_resource) \
            .option("es.nodes.wan.only", "false") \
            .mode("overwrite") \
            .save()
        logging.info("Dữ liệu đã được gửi thành công lên Elasticsearch!")
    except Exception as e:
        logging.error(f"Lỗi khi gửi dữ liệu lên Elasticsearch: {str(e)}")


def calculate_metrics_and_save(dataframe):
    metrics = calculate_metrics_per_ticker(dataframe)
    metrics.show(35, truncate=False)
    es_ready_data = metrics.withColumnRenamed("company_type", "companyType")
    save_to_elasticsearch(es_ready_data, "vn_30")

    save_to_cassandra(metrics, "stock_analytics", "historical_analysis")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("BatchLayerToCassandra") \
        .config("spark.cassandra.connection.host", "cassandra1") \
        .config("spark.cassandra.connection.port", "9042") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    input_path = "hdfs://namenode:8020/user/root/kafka_data"
    hadoop_data = spark.read.json(input_path)
    hadoop_data = hadoop_data.withColumnRenamed("companyType", "company_type")
    calculate_metrics_and_save(hadoop_data)
    spark.stop()