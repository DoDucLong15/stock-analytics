from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

session.execute("CREATE KEYSPACE stockdb\
    WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1}")

session.execute("USE stockdb")

session.execute("CREATE TABLE history_price (\
  ticker text,\
  high double,\
  low double,\
  open double,\
  close double,\
  volume double,\
  trading_date timestamp,\
  PRIMARY KEY (ticker, trading_date)\
) WITH CLUSTERING ORDER BY (trading_date DESC)")

session.execute("CREATE TABLE intraday (\
  ticker text,\
  type_order text,\
  volumn double,\
  price double,\
  prevPriceChange double,\
  trading_date timestamp,\
  PRIMARY KEY (ticker)\
)")

session.shutdown()