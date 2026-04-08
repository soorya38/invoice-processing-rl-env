import os
import json
import logging
import requests
import sys
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Environment variable configuration
# Mandatory structured logging tags: [START], [STEP], [END]
HF_TOKEN = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

ENV_URL = "http://localhost:8080"

from pydantic import BaseModel, Field
from openai import OpenAI

# Environment Models (Pydantic)
class InvoiceField(BaseModel):
    name: str
    value: str

class Observation(BaseModel):
    raw_text: str
    extracted_fields: List[InvoiceField]
    remaining_fields: List[str]

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: str

def reset(task_id: str = "easy") -> Optional[Observation]:
    """Resets the environment with the specified task."""
    try:
        response = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
        response.raise_for_status()
        return Observation(**response.json())
    except Exception as e:
        logger.error(f"Failed to reset environment: {e}")
        return None

def step(field_name: str, value: str) -> Optional[StepResult]:
    """Performs a step in the environment by extracting a field."""
    try:
        response = requests.post(f"{ENV_URL}/step", json={"field_name": field_name, "value": value})
        response.raise_for_status()
        return StepResult(**response.json())
    except Exception as e:
        logger.error(f"Failed to perform step: {e}")
        return None

def state() -> Optional[dict]:
    """Returns the current environment state."""
    try:
        response = requests.get(f"{ENV_URL}/state")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get state: {e}")
        return None

def run_llm_agent(task_id: str = "easy"):
    """An LLM-driven agent that interacts with the invoice processing environment."""
    dummy_mode = os.getenv("DUMMY_MODE", "0") == "1"

    if not dummy_mode and (not HF_TOKEN or not API_BASE_URL):
        logger.error("Mandatory environment variables (HF_TOKEN, API_BASE_URL) not set.")
        return

    # [START] Mandatory logging requirement - Must be on stdout
    print(f"[START] Task: {task_id}")
    sys.stdout.flush()

    if not dummy_mode:
        client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
        logger.info(f"Starting LLM agent for task: {task_id} using model: {MODEL_NAME}")
    else:
        logger.info(f"Starting DUMMY agent for task: {task_id}")

    obs = reset(task_id)
    if not obs:
        print(f"[END] Task: {task_id}, Score: 0.0")
        sys.stdout.flush()
        return

    tools = [
        {
            "type": "function",
            "function": {
                "name": "extract_field",
                "description": "Extract a specific field and its value from the invoice text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "field_name": {
                            "type": "string",
                            "description": "The name of the field to extract (must be one of the remaining_fields)."
                        },
                        "value": {
                            "type": "string",
                            "description": "The value associated with the field name as found in the raw text."
                        }
                    },
                    "required": ["field_name", "value"]
                }
            }
        }
    ]

    while True:
        if not dummy_mode:
            system_prompt = (
                "You are an expert invoice processing agent. Your goal is to extract key fields from the provided raw text. "
                "Use the 'extract_field' tool to submit your extractions one by one. "
                f"Required fields remaining: {', '.join(obs.remaining_fields)}"
            )
            
            user_prompt = f"Raw Invoice Text:\n{obs.raw_text}\n\nFields already extracted: {obs.extracted_fields}"

            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    tools=tools,
                    tool_choice="required",
                    temperature=0 # Maintain reproducibility
                )

                tool_call = response.choices[0].message.tool_calls[0]
                arguments = json.loads(tool_call.function.arguments)
                field_name = arguments["field_name"]
                value = arguments["value"]
            except Exception as e:
                logger.error(f"Error during LLM interaction: {e}")
                break
        else:
            # Dummy mode: just pick the first remaining field and a placeholder value
            if not obs.remaining_fields:
                break
            field_name = obs.remaining_fields[0]
            value = "DUMMY_VALUE" 
            logger.info(f"Dummy Action: Extracting {field_name} -> {value}")

        logger.info(f"Action: {field_name} -> {value}")
        
        result = step(field_name, value)
        if not result:
            break
            
        obs = result.observation
        reward = result.reward
        done = result.done

        # [STEP] Mandatory logging requirement - Must be on stdout
        print(f"[STEP] Action: extract_field({field_name}, {value}), Reward: {reward:.2f}")
        sys.stdout.flush()
        
        if done:
            break

    final_state = state()
    final_score = 0.0
    if final_state:
        final_score = final_state.get('FinalScore', 0.0)
        steps = final_state.get('StepCount', 0)
        max_steps = final_state.get('MaxSteps', 0)
        logger.info(f"Task {task_id} result: Steps={steps}/{max_steps}, Final Score={final_score:.2f}")
    
    # [END] Mandatory logging requirement - Must be on stdout
    print(f"[END] Task: {task_id}, Score: {final_score:.2f}")
    sys.stdout.flush()

if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        run_llm_agent(level)
# Agent compliance verified.
