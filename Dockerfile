# Step 1: Build the Go binary
FROM golang:1.24-alpine AS builder

WORKDIR /app

# Copy go.mod and handle dependencies
COPY server/go.mod ./
RUN go mod tidy

# Copy the rest of the server code
COPY server/ ./server/

# Build the main server binary
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./server/main.go

# Step 2: Create a minimal runtime image
FROM alpine:latest

WORKDIR /app
COPY --from=builder /app/main .

# Expose the API port
EXPOSE 8080

# Run the server
CMD ["./main"]
