#!/bin/bash
set -e
GREEN='\033[0;32m'
NC='\033[0m'
# Validate Python script syntax
echo "Checking Python inference script syntax..."
python3 -m py_compile inference.py
echo -e "${GREEN}[✔️] Python syntax check passed${NC}"

# End-to-End Validation
echo -e "${GREEN}Starting End-to-End validation...${NC}"

# Check for dependencies
python3 -m pip install -q requests pydantic openai --break-system-packages || echo "Warning: Could not install dependencies, skipping runtime check"

# Start Go server in background
echo "Starting Go server..."
go run server/main.go > /tmp/server.log 2>&1 &
SERVER_PID=$!

# Wait for server to be ready
echo "Waiting for server to start on port 8080..."
for i in {1..10}; do
    if curl -s http://localhost:8080/ > /dev/null; then
        echo -e "${GREEN}[✔️] Server is up and responding to root ping${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}[❌] Server failed to start or root ping failed${NC}"
        kill $SERVER_PID
        exit 1
    fi
    sleep 1
done

# Run inference.py in DUMMY_MODE
echo "Running inference.py in DUMMY_MODE..."
DUMMY_MODE=1 python3 inference.py > /tmp/inference.log 2>&1
required_files=( "server/main.go" "inference.py" "openenv.yaml" "Dockerfile" )
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then echo "[✔️] Found $file"; else exit 1; fi
done
echo "Testing Go server compilation..."
(cd server && go build -o /dev/null .)
echo -e "${GREEN}[✔️] Go build successful${NC}"
