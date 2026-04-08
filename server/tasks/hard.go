package tasks

import (
	"rl_env/server/env"
)

func init() {
	Register("hard", GenerateHardTask)
}

// GenerateHardTask returns a hard invoice with complex layout or noise.
func GenerateHardTask() *env.Invoice {
	return &env.Invoice{
		ID: "hard-001",
		RawText: `--- CONFIDENTIAL PURCHASE ORDER ---
REF NO: PO-8872-XYZ
DATE OF ISSUE: 2023/12/25
SUPPLY PARTNER: Tech Innovators Inc.
HQ ADDRESS: 123 Silicon Valley Way, CA

* NOTE: Please refer to shipment date for delivery schedules.
* SHIPMENT DATE: 2024/01/10

BILLING SUMMARY (Internal Code: PRX-99)
=======================================
DESCRIPTION      | QTY | UNIT PRICE | TOTAL
=======================================
Server Farm A1   | 1   | 10000.00   | 10000.00
Maintenance Svc  | 12  | 41.67      | 500.04
=======================================
NET AMOUNT (SUBTOTAL): 10500.04
TAXABLE VAT (15%): 1575.01
EXCISE DUTY: 100.00
GRAND TOTAL PAYABLE: 12175.05

REMITTANCE INFO (OVERDUE AFTER 30 DAYS):
BANK: GLOBAL TECH BANK
SWIFT: TECHINV44
ACC: 9988776655
Please use REF NO PO-8872-XYZ for all queries.`,
		GroundTruth: []env.Field{
			{Name: "RefNumber", Value: "PO-8872-XYZ"},
			{Name: "Supplier", Value: "Tech Innovators Inc."},
			{Name: "IssueDate", Value: "2023/12/25"},
			{Name: "ShipmentDate", Value: "2024/01/10"},
			{Name: "NetAmount", Value: "10500.04"},
			{Name: "VAT", Value: "1575.01"},
			{Name: "ExciseDuty", Value: "100.00"},
			{Name: "Total", Value: "12175.05"},
			{Name: "SWIFT", Value: "TECHINV44"},
		},
	}
}
