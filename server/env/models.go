package env

// Field represents a single piece of information extracted from an invoice.
type Field struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

// Invoice represents the domain object with ground truth data.
type Invoice struct {
	ID          string  `json:"id"`
	RawText     string  `json:"raw_text"`
	GroundTruth []Field `json:"ground_truth"`
}

// Observation is what the RL agent sees at each step.
type Observation struct {
	RawText         string   `json:"raw_text"`
	ExtractedFields []Field  `json:"extracted_fields"`
	RemainingFields []string `json:"remaining_fields"`
}

// Action is the move taken by the agent.
type Action struct {
	FieldName string `json:"field_name"`
	Value     string `json:"value"`
}

// StepResult contains the outcome of an environment step.
type StepResult struct {
	Observation Observation `json:"observation"`
	Reward      float64     `json:"reward"`
	Done        bool        `json:"done"`
	Info        string      `json:"info"`
}

// EnvironmentState maintains the internal state of the current session.
type EnvironmentState struct {
	CurrentInvoice *Invoice
	Extracted      []Field
	StepCount      int
	MaxSteps       int
	LastAction     *Action
	FinalScore     float64
	Done           bool
}
