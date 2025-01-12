package main

import (
	"encoding/json"
	"log"
	"math/rand"
	"time"

	"github.com/confluentinc/confluent-kafka-go/kafka"
)

type StockData struct {
	Ticker          string  `json:"ticker"`
	Time            string  `json:"time"`
	OrderType       string  `json:"orderType"`
	InvestorType    string  `json:"investorType"`
	Volume          int     `json:"volume"`
	AveragePrice    float64 `json:"averagePrice"`
	OrderCount      int     `json:"orderCount"`
	PrevPriceChange float64 `json:"prevPriceChange"`
}

var tickers = []string{"MSN"}
var orderTypes = []string{"Buy Up", "Sell Down"}
var investorTypes = []string{"SHEEP", "WOLF", "SMART"}

func generateStockData() StockData {
	ticker := tickers[rand.Intn(len(tickers))]
	orderType := orderTypes[rand.Intn(len(orderTypes))]
	investorType := investorTypes[rand.Intn(len(investorTypes))]
	volume := rand.Intn(5000) + 100
	averagePrice := float64(rand.Intn(100000)+10000) / 100.0
	orderCount := rand.Intn(10) + 1
	prevPriceChange := float64(rand.Intn(2000)-1000) / 100.0

	return StockData{
		Ticker:          ticker,
		Time:            time.Now().Format("2006-01-02 15:04:05"),
		OrderType:       orderType,
		InvestorType:    investorType,
		Volume:          volume,
		AveragePrice:    averagePrice,
		OrderCount:      orderCount,
		PrevPriceChange: prevPriceChange,
	}
}

func produceKafkaMessage(producer *kafka.Producer, topic string, data StockData) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		log.Printf("Error marshaling data: %s", err)
		return
	}

	err = producer.Produce(&kafka.Message{
		TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
		Key:            []byte(data.Ticker),
		Value:          jsonData,
	}, nil)

	if err != nil {
		log.Printf("Failed to produce message: %s", err)
	} else {
		log.Printf("Produced message to topic %s: %s", topic, string(jsonData))
	}

	go producer.Flush(1000)
}

func main() {
	rand.Seed(time.Now().UnixNano())

	brokers := "localhost:9093,localhost:9095,localhost:9097"
	topic := "stock_realtime4"

	producer, err := kafka.NewProducer(&kafka.ConfigMap{"bootstrap.servers": brokers})
	if err != nil {
		log.Fatalf("Failed to create Kafka producer: %s", err)
	}
	defer producer.Close()

	log.Println("Kafka producer created successfully")

	for {
		data := generateStockData()
		produceKafkaMessage(producer, topic, data)

		time.Sleep(1 * time.Second)
	}
}
