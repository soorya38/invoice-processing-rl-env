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
    if not HF_TOKEN or not API_BASE_URL:
        logger.error("Mandatory environment variables (HF_TOKEN, API_BASE_URL) not set.")
        return

    print(f"Starting Task: {task_id}")
    client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

    obs = reset(task_id)
    if not obs:
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
        system_prompt = "Process invoice text."
        user_prompt = f"Raw Invoice Text:\n{obs.raw_text}"

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

            result = step(field_name, value)
            if not result:
                break
            obs = result.observation
            if result.done:
                break
        except Exception as e:
            logger.error(f"Error: {e}")
            break
