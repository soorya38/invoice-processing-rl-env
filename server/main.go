package main

import (
	"log"
	"net/http"
	"rl_env/server/handlers"

	// Register tasks
	_ "rl_env/server/tasks"
)

func main() {
	// Register HTTP routes
	http.HandleFunc("/reset", handlers.HandleReset)
	http.HandleFunc("/step", handlers.HandleStep)
	http.HandleFunc("/state", handlers.HandleState)
	http.HandleFunc("/health", handlers.HandleHealth)
	http.HandleFunc("/", handlers.HandleHealth) // Root health check

	port := ":8080"
	log.Printf("Invoice Processing OpenEnv Server starting on %s...", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
