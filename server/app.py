import subprocess
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server-wrapper")

def main():
    """
    Main entry point for the OpenEnv server.
    This is a Python wrapper that launches the core Go server binary.
    """
    # In Docker, the Go binary is compiled and placed in /app/main
    # Locally, we can try to find it or use 'go run'
    
    binary_path = "/app/main" # Standard path in Docker
    
    if not os.path.exists(binary_path):
        # Fallback for local development
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_binary = os.path.join(base_dir, "main")
        
        if os.path.exists(local_binary):
            binary_path = local_binary
        else:
            logger.info("Go binary not found, attempting to run via 'go run'...")
            binary_path = "go run server/main.go"

    logger.info(f"Starting Go server via binary: {binary_path}")
    
    try:
        # Pass through environment variables and start the server
        process = subprocess.Popen(
            binary_path,
            shell=True,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        process.wait()
    except KeyboardInterrupt:
        logger.info("Stopping Go server...")
        process.terminate()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
