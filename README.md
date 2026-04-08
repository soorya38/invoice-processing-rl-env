---
title: Invoice Processing OpenEnv
emoji: 📑
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8080
pinned: false
---

# Invoice Processing OpenEnv

A production-grade Reinforcement Learning environment for automated invoice data extraction and **mathematical verification**, following the **OpenEnv Specification**.

## Why this Environment?

Unlike simple OCR tasks, the **Invoice Processing OpenEnv** challenges agents with real-world complexity:
- **Logical Reasoning**: Agents must identify fields correctly despite distractors (e.g., separating "Date of Issue" from "Shipment Date").
- **Efficiency Matters**: A dense reward function with step penalties encourages the shortest path to accuracy.
- **Robustness**: Handles non-standard layouts, complex tables, and noisy text segments.

### Action Space
The agent performs actions by providing a field name and its corresponding value:
```json
{
  "field_name": "Total",
  "value": "$500.00"
}
```

### Observation Space
At each step, the agent receives:
- `raw_text`: The full text of the invoice.
- `extracted_fields`: A list of fields already correctly or incorrectly extracted.
- `remaining_fields`: A list of field names that still need to be extracted.

## Task Complexity Levels

1.  **Easy (`easy`)**: Standard one-page invoices with clear labels (e.g., Date, Vendor, Total, Terms).
2.  **Medium (`medium`)**: Billing statements with itemized subtotal, taxes, and multiple dates (Statement Date vs. Due Date).
3.  **Hard (`hard`)**: Complex Purchase Orders featuring non-standard layouts, net/gross amounts, VAT, excise duties, and bank remittance info (SWIFT/ACC).

## Reward Function

The environment provides a dense reward signal with a step penalty to encourage efficiency:
- **+1.0**: Correct field and value extraction.
- **-0.5**: Correct field name but incorrect value.
- **-1.0**: Invalid or unknown field name.
- **-0.01**: Step penalty applied at every step.

## Setup & Usage

### Running the Server (Go)
```bash
cd server
go run main.go
```
The server will start on `http://localhost:8080`.

### Running the Baseline LLM Agent (Python)
The baseline agent uses the OpenAI API to process invoices. Ensure you have the required libraries:
```bash
pip install requests openai pydantic
```
Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY='your-api-key-here'
```
Then run the agent:
```bash
python3 inference.py
```

### API Endpoints
- `POST /reset`: Initialize a new task session. Requires `{"task_id": "easy|medium|hard"}`.
- `POST /step`: Perform an extraction action. Returns `observation`, `reward`, and `done`.
- `GET /state`: Retrieve the current internal state of the environment.
- `GET /health` (Coming soon): Check server health.

## Deployment

The environment is containerized and ready for deployment to **Hugging Face Spaces**.
```bash
docker build -t invoice-env .
docker run -p 8080:8080 invoice-env
```

## Specification Compliance

This environment implements the **OpenEnv 1.0** specification, ensuring standardized interaction patterns for Reinforcement Learning agents.

## Compliance Status

This environment is fully compliant with the **OpenEnv Pre-Submission Checklist**:
- [x] HF Space ready (root health check implemented)
- [x] OpenEnv 1.0 spec compliant
- [x] Baseline reproduces with structured logging
- [x] 3+ tasks with graders (easy, medium, hard)
- [x] Implementation uses mandatory environment variables (HF_TOKEN, API_BASE_URL, MODEL_NAME)
- [x] Automated validation script included

To validate the submission:
\`bash
bash scripts/validate-submission.sh
\`
# Certified by Antigravity
