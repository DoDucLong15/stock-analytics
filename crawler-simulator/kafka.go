package main

//
//import (
//	"encoding/json"
//	"fmt"
//	"log"
//
//	"github.com/confluentinc/confluent-kafka-go/kafka"
//)
//
//// ProduceKafkaMessage gửi dữ liệu tới Kafka
//func ProduceKafkaMessage(topic, key string, message interface{}) error {
//	// Cấu hình Kafka producer
//	producer, err := kafka.NewProducer(&kafka.ConfigMap{
//		"bootstrap.servers": "localhost:9092", // Thay bằng Kafka broker thực tế của bạn
//	})
//	if err != nil {
//		return fmt.Errorf("không thể tạo Kafka producer: %v", err)
//	}
//	defer producer.Close()
//
//	// Chuyển message thành JSON
//	jsonMessage, err := json.Marshal(message)
//	if err != nil {
//		return fmt.Errorf("lỗi mã hóa JSON: %v", err)
//	}
//
//	// Gửi message tới Kafka
//	deliveryChan := make(chan kafka.Event)
//	err = producer.Produce(&kafka.Message{
//		TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
//		Key:            []byte(key),
//		Value:          jsonMessage,
//	}, deliveryChan)
//	if err != nil {
//		return fmt.Errorf("lỗi khi gửi message tới Kafka: %v", err)
//	}
//
//	// Đợi xác nhận gửi thành công
//	e := <-deliveryChan
//	m := e.(*kafka.Message)
//
//	if m.TopicPartition.Error != nil {
//		log.Printf("Gửi message thất bại: %v\n", m.TopicPartition.Error)
//	} else {
//		log.Printf("Message gửi thành công: Key=%s, Topic=%s\n", key, *m.TopicPartition.Topic)
//	}
//
//	close(deliveryChan)
//	return nil
//}
