package main

//
//import (
//	"math/rand"
//	"time"
//
//	"github.com/brianvoe/gofakeit/v6"
//)
//
//// StockData là cấu trúc dữ liệu mô phỏng giao dịch intraday
//type StockData struct {
//	Ticker          string  `json:"ticker"`
//	Time            string  `json:"time"`
//	OrderType       string  `json:"orderType"`
//	InvestorType    string  `json:"investorType"`
//	Volume          int64   `json:"volume"`
//	AveragePrice    float64 `json:"averagePrice"`
//	OrderCount      int     `json:"orderCount"`
//	PrevPriceChange float64 `json:"prevPriceChange"`
//}
//
//// GenerateIntradayData tạo một giao dịch intraday ngẫu nhiên
//func GenerateIntradayData(ticker string, basePrice float64) StockData {
//	gofakeit.Seed(time.Now().UnixNano()) // Khởi tạo seed để tạo dữ liệu ngẫu nhiên
//
//	// Các giá trị ngẫu nhiên
//	orderTypes := []string{"Buy Up", "Sell Down"}
//	investorTypes := []string{"SHEEP", "WOLF"}
//	orderType := orderTypes[rand.Intn(len(orderTypes))]
//	investorType := investorTypes[rand.Intn(len(investorTypes))]
//	volume := int64(gofakeit.Number(100, 10000))
//	priceChange := gofakeit.Float64Range(-100, 100)
//	orderCount := gofakeit.Number(1, 5)
//
//	// Tính giá trung bình
//	averagePrice := basePrice + priceChange
//
//	// Trả về giao dịch intraday
//	return StockData{
//		Ticker:          ticker,
//		Time:            time.Now().Format("2006-01-02 15:04:05"),
//		OrderType:       orderType,
//		InvestorType:    investorType,
//		Volume:          volume,
//		AveragePrice:    averagePrice,
//		OrderCount:      orderCount,
//		PrevPriceChange: priceChange,
//	}
//}
