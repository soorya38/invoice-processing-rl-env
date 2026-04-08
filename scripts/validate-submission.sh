#!/bin/bash
set -e
GREEN='\033[0;32m'
NC='\033[0m'
echo -e "${GREEN}Starting validation...${NC}"
required_files=( "server/main.go" "inference.py" "openenv.yaml" "Dockerfile" )
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then echo "[✔️] Found $file"; else exit 1; fi
done
