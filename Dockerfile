# Step 1: Build the Go binary
FROM golang:1.24-alpine AS builder

WORKDIR /app

# Copy the entire server contents into the root of the builder
COPY server/ ./

# Tidy dependencies and build (within the module root)
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -o main main.go

# Step 2: Create the runtime image
# Using python:3.11-slim to ensure Python is available for the evaluator
FROM python:3.11-slim

WORKDIR /app

# Copy the Go binary
COPY --from=builder /app/main .

# Copy compliance files
COPY pyproject.toml uv.lock ./
COPY server/app.py ./server/app.py
COPY inference.py ./
COPY openenv.yaml ./
COPY README.md ./

# Install python dependencies required by inference.py
RUN pip install --no-cache-dir requests pydantic openai python-dotenv

# Fix 'python' command path for script robustness
RUN ln -s /usr/local/bin/python3 /usr/bin/python || true

# Expose the API port
EXPOSE 8080

# Run the server
CMD ["./main"]
