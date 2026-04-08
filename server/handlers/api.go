package handlers

import (
	"encoding/json"
	"net/http"
	"rl_env/server/env"
	"rl_env/server/tasks"
)

var currentEnv = &env.Environment{}

// HandleReset resets the environment with a specific task.
func HandleReset(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	type ResetRequest struct {
		TaskID string `json:"task_id"`
	}

	var req ResetRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	invoice := tasks.GetTask(req.TaskID)
	if invoice == nil {
		http.Error(w, "Task not found", http.StatusNotFound)
		return
	}

	obs := currentEnv.Reset(invoice)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(obs)
}

// HandleStep performs an extraction step in the environment.
func HandleStep(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var action env.Action
	if err := json.NewDecoder(r.Body).Decode(&action); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	result, err := currentEnv.Step(action)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

// HandleHealth returns the server health status.
func HandleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "ok", "message": "Invoice Processing OpenEnv Server is running"})
}

// HandleState returns the current environment state.
func HandleState(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(currentEnv.State)
}
