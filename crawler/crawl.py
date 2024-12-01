from confluent_kafka import Producer
from vnstock import *
import pandas as pd
import time
from datetime import datetime, timedelta
import json
import threading

def produce_kafka_json(bootstrap_servers, topic_name, symbol, json_message):
  try:
    producer = Producer({'bootstrap.servers': bootstrap_servers})
    producer.produce(topic_name, value=json_message.encode('utf-8'), key=symbol.encode('utf-8'), callback=delivery_report)
    producer.flush()
  except Exception as e:
    print(f"Error producing message: {e}")

def delivery_report(err, msg):
  """Callback được gọi khi tin nhắn được gửi thành công hoặc gặp lỗi."""
  if err is not None:
    print('Gửi tin nhắn thất bại: {}'.format(err))
  else:
    print('Tin nhắn được gửi thành công: {}'.format(msg.key().decode('utf-8')))

def get_stock_data(symbol):
  today = datetime.now()
  start_date_this_week = today - timedelta(days=today.weekday())
  start_date_last_week = start_date_this_week - timedelta(days=7)
  end_date_last_week = start_date_last_week + timedelta(days=6)
  start_date_last_week_str = start_date_last_week.strftime('%Y-%m-%d')
  end_date_last_week_str = end_date_last_week.strftime('%Y-%m-%d')

  info_df = company_overview(symbol)

  df = stock_historical_data(
      symbol=symbol,
      start_date=start_date_last_week_str,
      end_date=end_date_last_week_str,
      resolution='1',
      type='stock',
      beautify=True
  )
  df['time'] = pd.to_datetime(df['time'])
  df['time'] = df['time'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if not pd.isnull(x) else None)
  df = df.assign(companyType=info_df['companyType'].iloc[0])

  json_data = df.to_json(date_format='iso', orient='records')
  return json_data

def get_stock_data_intraday(symbol):
  df = stock_intraday_data(
      symbol=symbol,
      page_size=100,
      investor_segment=True
  )
  df['time'] = pd.to_datetime(df['time'])
  df['time'] = df['time'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if not pd.isnull(x) else None)


  json_data = df.to_json(date_format='iso', orient='records')
  return json_data

def jobCrawlVn30Data(kafka_topic, bootstrap_servers):


  symbol_array = ["ACB","BCM","BID","BVH","CTG",
                  "FPT","GAS","GVR","HDB","HPG","MBB","MSN",
                  "MWG","PLX","POW","SAB","SHB","SSB","SSI",
                  "STB","TCB","TPB","VCB","VHM","VIB","VIC",
                  "VJC","VNM","VPB","VRE"]
  while True:
    for symbol in symbol_array:
      json_data = get_stock_data(symbol)
      print(json_data)
      produce_kafka_json(bootstrap_servers, kafka_topic, symbol, json_data)
      time.sleep(2)
    break

def jobCrawlStockDataRealtime(symbol, kafka_topic, bootstrap_servers):
  while True:
    stock_data = get_stock_data_intraday(symbol)
    print(stock_data)
    produce_kafka_json(bootstrap_servers, kafka_topic, symbol, stock_data)
    time.sleep(90)

if __name__ == "__main__":
  bootstrap_servers = 'kafka:9092,kafka:9094,kafka:9096'
  kafka_topic_vn30 = 'vn30'  #
  kafka_topic_realtime = 'stock_realtime4'

  t1 = threading.Thread(target=jobCrawlVn30Data, args=(kafka_topic_vn30, bootstrap_servers))
  t2 = threading.Thread(target=jobCrawlStockDataRealtime, args=('MSN', kafka_topic_realtime, bootstrap_servers))

  t1.start()
  t2.start()

  t1.join()
  t2.join()