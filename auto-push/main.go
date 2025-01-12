package main

import (
	"github.com/robfig/cron/v3"
	"log"
	"os/exec"
	"time"
)

func main() {
	c := cron.New(cron.WithSeconds())

	cronExpression := "0 25 10 * * 6"

	_, err := c.AddFunc(cronExpression, func() {
		cmd := exec.Command("docker", "exec", "stock-analytics-spark-submit-app-1", "spark-submit", "--packages", "org.elasticsearch:elasticsearch-spark-30_2.12:7.15.2,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0", "./hadoop_to_elastics.py")

		output, err := cmd.CombinedOutput()

		if err != nil {
			log.Printf("Error running spark-submit: %v\nOutput: %s", err, output)
		} else {
			log.Printf("Spark job triggered successfully at %s\nOutput: %s", time.Now().Format(time.RFC3339), output)
		}
	})

	if err != nil {
		log.Fatalf("Error adding cron job: %v", err)
	}

	c.Start()

	select {}
}
