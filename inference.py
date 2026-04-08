import os
import json
import logging
import requests
import sys
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI

# Configure logging to stderr to keep stdout clean for mandatory tags
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)

# Environment variable configuration (Aligned with Sample Script)
HF_TOKEN = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
BENCHMARK = os.getenv("MY_ENV_V4_BENCHMARK", "invoice_processing")

ENV_URL = "http://localhost:8080"
SUCCESS_SCORE_THRESHOLD = 0.9

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

def reset(task_id: str) -> Optional[Observation]:
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

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step_n: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step_n} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

def run_agent(task_id: str):
    """An LLM-driven agent that interacts with the invoice processing environment."""
    dummy_mode = os.getenv("DUMMY_MODE", "0") == "1"

    if not dummy_mode and not HF_TOKEN:
        logger.error("Mandatory environment variable HF_TOKEN not set.")
        return

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    if not dummy_mode:
        client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
        logger.info(f"Starting LLM agent for task: {task_id}")
    else:
        logger.info(f"Starting DUMMY agent for task: {task_id}")

    obs = reset(task_id)
    if not obs:
        log_end(success=False, steps=0, score=0.0, rewards=[])
        return

    rewards_list = []
    steps_taken = 0
    done = False
    
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

    while not done:
        steps_taken += 1
        action_desc = ""
        
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
                    temperature=0
                )

                tool_call = response.choices[0].message.tool_calls[0]
                arguments = json.loads(tool_call.function.arguments)
                field_name = arguments["field_name"]
                value = arguments["value"]
                action_desc = f"extract_field('{field_name}')"
            except Exception as e:
                logger.error(f"Error during LLM interaction: {e}")
                log_step(step_n=steps_taken, action="error", reward=0.0, done=True, error=str(e))
                # Break to summary
                break
        else:
            if not obs.remaining_fields:
                break
            field_name = obs.remaining_fields[0]
            value = "DUMMY_VALUE" 
            action_desc = f"extract_field('{field_name}')"

        result = step(field_name, value)
        if not result:
            break
            
        obs = result.observation
        reward = result.reward
        done = result.done
        rewards_list.append(reward)
        
        log_step(step_n=steps_taken, action=action_desc, reward=reward, done=done, error=None)

    final_state = state()
    final_score = 0.0
    if final_state:
        final_score = final_state.get('FinalScore', 0.0)
    
    success = final_score >= SUCCESS_SCORE_THRESHOLD
    log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards_list)

if __name__ == "__main__":
    for difficulty in ["easy", "medium", "hard"]:
        run_agent(difficulty)
