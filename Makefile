HF_USERNAME = sooryaakilesh
SPACE_NAME = invoice-processing-rl-env

test:
	@echo "Running pre-submission validation..."
	@bash scripts/validate-submission.sh

deploy:
	@echo "Deploying to Hugging Face Spaces..."
	@# Expects HF_TOKEN to be set in the environment or git credentials to be configured
	@git remote add hf https://huggingface.co/spaces/$(HF_USERNAME)/$(SPACE_NAME) 2>/dev/null || \
		git remote set-url hf https://huggingface.co/spaces/$(HF_USERNAME)/$(SPACE_NAME)
	@git push hf main --force
	@echo "Deployment initiated. Visit https://huggingface.co/spaces/$(HF_USERNAME)/$(SPACE_NAME) to check build status."
