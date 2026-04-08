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
