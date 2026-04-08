import os
import requests
from inference import Observation, StepResult, log_start, log_step, log_end

ENV_URL = os.getenv("ENV_URL", "https://sooryaakilesh-invoice-processing-rl-env.hf.space")
TASK_ID = "easy"

def run_faulty_agent():
    print(f"--- STARTING FAULTY AGENT TEST AGAINST {ENV_URL} ---")
    
    # 1. Start session
    log_start(task=TASK_ID, env="invoice_processing", model="FaultyAgent-v1")
    
    # Reset
    response = requests.post(f"{ENV_URL}/reset", json={"task_id": TASK_ID})
    obs = Observation(**response.json())
    
    rewards = []
    
    # ACTION 1: Correct choice (expected reward: 0.99)
    field = obs.remaining_fields[0]
    print(f"\n[TEST] Action 1: Extracting CORRECT field '{field}'")
    res = requests.post(f"{ENV_URL}/step", json={"field_name": field, "value": "Vendor 123"}).json() # Dummy but matches ground truth pattern? No, let's assume it's wrong value.
    result = StepResult(**res)
    log_step(1, f"extract_field('{field}')", result.reward, result.done, None)
    rewards.append(result.reward)

    # ACTION 2: WRONG VALUE (expected reward: -0.51)
    field = result.observation.remaining_fields[0]
    print(f"\n[TEST] Action 2: Extracting field '{field}' with intentional WRONG VALUE")
    res = requests.post(f"{ENV_URL}/step", json={"field_name": field, "value": "TOTALLY_WRONG"}).json()
    result = StepResult(**res)
    log_step(2, f"extract_field('{field}')", result.reward, result.done, None)
    rewards.append(result.reward)

    # ACTION 3: DUPLICATE EXTRACTION (expected reward: -1.51)
    print(f"\n[TEST] Action 3: Attempting DUPLICATE extraction of first field")
    res = requests.post(f"{ENV_URL}/step", json={"field_name": obs.remaining_fields[0], "value": "Anything"}).json()
    result = StepResult(**res)
    log_step(3, "duplicate_action", result.reward, result.done, None)
    rewards.append(result.reward)

    # 2. Get Final State
    final_state = requests.get(f"{ENV_URL}/state").json()
    score = final_state.get('FinalScore', 0.0)
    
    log_end(success=False, steps=3, score=score, rewards=rewards)

if __name__ == "__main__":
    run_faulty_agent()
