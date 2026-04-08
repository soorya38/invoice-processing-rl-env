package tasks

import (
	"rl_env/server/env"
)

func init() {
	Register("easy", GenerateEasyTask)
}

// GenerateEasyTask returns a simple invoice task.
func GenerateEasyTask() *env.Invoice {
	return &env.Invoice{
		ID: "easy-001",
		RawText: `INVOICE #INV-101
Date: 2023-10-01
Vendor: ACME Corp
Total: $500.00
Payment Terms: Net 30`,
		GroundTruth: []env.Field{
			{Name: "InvoiceNumber", Value: "INV-101"},
			{Name: "Date", Value: "2023-10-01"},
			{Name: "Vendor", Value: "ACME Corp"},
			{Name: "Total", Value: "$500.00"},
			{Name: "Terms", Value: "Net 30"},
		},
	}
}
