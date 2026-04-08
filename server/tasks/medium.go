package tasks

import (
	"rl_env/server/env"
)

func init() {
	Register("medium", GenerateMediumTask)
}

// GenerateMediumTask returns a medium difficulty invoice with multiple items.
func GenerateMediumTask() *env.Invoice {
	return &env.Invoice{
		ID: "medium-001",
		RawText: `BILLING STATEMENT
Billed To: Global Logistics Inc.
Statement Date: Nov 15, 2023
Due Date: Dec 15, 2023

Line Items:
1. International Shipping   $200.00
2. Custom Clearance        $50.00
3. Insurance               $10.00

Subtotal: $260.00
Tax (5%): $13.00
Grand Total: $273.00`,
		GroundTruth: []env.Field{
			{Name: "Customer", Value: "Global Logistics Inc."},
			{Name: "StatementDate", Value: "Nov 15, 2023"},
			{Name: "DueDate", Value: "Dec 15, 2023"},
			{Name: "Subtotal", Value: "$260.00"},
			{Name: "Tax", Value: "$13.00"},
			{Name: "Total", Value: "$273.00"},
		},
	}
}
