package env

import (
	"errors"
	"fmt"
	"strings"
)

// Environment handles the lifecycle and state transitions of an invoice processing task.
type Environment struct {
	State EnvironmentState
}

// Reset initializes the environment with a new invoice.
func (e *Environment) Reset(invoice *Invoice) Observation {
	e.State = EnvironmentState{
		CurrentInvoice: invoice,
		Extracted:      []Field{},
		StepCount:      0,
		MaxSteps:       len(invoice.GroundTruth) * 2, // Allow 2x attempts per field
		Done:           false,
	}
	return e.getObservation()
}

// Step applies an action and returns the resulting observation and reward.
func (e *Environment) Step(action Action) (StepResult, error) {
	if e.State.Done {
		return StepResult{}, errors.New("environment is already done")
	}

	// Increment step count
	e.State.StepCount++

	// Add action to extracted fields
	e.State.Extracted = append(e.State.Extracted, Field{
		Name:  action.FieldName,
		Value: action.Value,
	})

	// Calculate reward
	reward := e.calculateReward(action)
	// Apply step penalty
	reward -= 0.01

	// Check if all fields are extracted or limit reached
	if len(e.State.Extracted) >= len(e.State.CurrentInvoice.GroundTruth) || e.State.StepCount >= e.State.MaxSteps {
		e.State.Done = true
	}

	info := fmt.Sprintf("Processed field: %s", action.FieldName)
	if e.State.StepCount >= e.State.MaxSteps || e.State.Done {
		if e.State.StepCount >= e.State.MaxSteps {
			info = "Episode ended: Maximum steps reached"
			e.State.Done = true
		}
		e.State.FinalScore = e.CalculateScore(e.State.Extracted, e.State.CurrentInvoice.GroundTruth)
	}

	return StepResult{
		Observation: e.getObservation(),
		Reward:      reward,
		Done:        e.State.Done,
		Info:        info,
	}, nil
}

func (e *Environment) getObservation() Observation {
	if e.State.CurrentInvoice == nil {
		return Observation{}
	}

	remaining := []string{}
	extractedMap := make(map[string]bool)
	for _, f := range e.State.Extracted {
		extractedMap[f.Name] = true
	}

	for _, f := range e.State.CurrentInvoice.GroundTruth {
		if !extractedMap[f.Name] {
			remaining = append(remaining, f.Name)
		}
	}

	return Observation{
		RawText:         e.State.CurrentInvoice.RawText,
		ExtractedFields: e.State.Extracted,
		RemainingFields: remaining,
	}
}

func (e *Environment) calculateReward(action Action) float64 {
	// Penalty for repeating the same field extraction
	for _, f := range e.State.Extracted[:len(e.State.Extracted)-1] {
		if f.Name == action.FieldName {
			return -1.5 // Extra penalty for redundant extraction
		}
	}

	for _, f := range e.State.CurrentInvoice.GroundTruth {
		if f.Name == action.FieldName {
			if f.Value == action.Value {
				return 1.0 // Correct extraction
			}
			return -0.5 // Incorrect value
		}
	}
	return -1.0 // Unknown field
}

// CalculateScore computes the accuracy of extracted fields against ground truth.
func (e *Environment) CalculateScore(extracted []Field, groundTruth []Field) float64 {
	if len(groundTruth) == 0 {
		return 0.0
	}

	correct := 0
	gtMap := make(map[string]string)
	for _, f := range groundTruth {
		gtMap[f.Name] = f.Value
	}

	for _, f := range extracted {
		if val, ok := gtMap[f.Name]; ok {
			// Normalize strings for comparison
			if strings.TrimSpace(strings.ToLower(val)) == strings.TrimSpace(strings.ToLower(f.Value)) {
				correct++
			}
		}
	}

	return float64(correct) / float64(len(groundTruth))
}
