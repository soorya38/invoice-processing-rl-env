package main

import (
	"log"
	"net/http"
	"rl_env/server/handlers"

	// Register tasks
	_ "rl_env/server/tasks"
)

func enableCors(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next(w, r)
	}
}

func main() {
	// Register HTTP routes with CORS support
	http.HandleFunc("/reset", enableCors(handlers.HandleReset))
	http.HandleFunc("/step", enableCors(handlers.HandleStep))
	http.HandleFunc("/state", enableCors(handlers.HandleState))
	http.HandleFunc("/health", enableCors(handlers.HandleHealth))
	http.HandleFunc("/", enableCors(handlers.HandleHealth)) // Root health check

	port := ":8080"
	log.Printf("Invoice Processing OpenEnv Server starting on %s...", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
