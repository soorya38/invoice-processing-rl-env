# Step 1: Build the Go binary
FROM golang:1.24-alpine AS builder

WORKDIR /app

# Copy the entire server contents into the root of the builder
COPY server/ ./

# Tidy dependencies and build (within the module root)
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -o main main.go

# Step 2: Create a minimal runtime image
FROM alpine:latest

WORKDIR /app
COPY --from=builder /app/main .

# Expose the API port
EXPOSE 8080

# Run the server
CMD ["./main"]
