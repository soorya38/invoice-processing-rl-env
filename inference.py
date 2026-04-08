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
