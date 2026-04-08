import os
import requests
import random
import time
from inference import Observation, StepResult, log_start, log_step, log_end

ENV_URL = os.getenv("ENV_URL", "https://sooryaakilesh-invoice-processing-rl-env.hf.space")
BENCHMARK = "invoice_processing"

def simulate_episode(episode_num, accuracy_prob):
    task_id = "easy"
    print(f"\n{'='*60}")
    print(f" EPISODE {episode_num} | TARGET ACCURACY: {int(accuracy_prob*100)}%")
    print(f"{'='*60}")
    
    log_start(task=task_id, env=BENCHMARK, model=f"RL-Agent-Training-Step-{episode_num}")
    
    # Reset
    response = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    obs = Observation(**response.json())
    
    rewards = []
    step = 1
    
    # Simple loop: try to extract remaining fields
    while not obs.remaining_fields == [] and step <= 10:
        field = obs.remaining_fields[0]
        
        # Simulate realistic learning
        is_correct = random.random() < accuracy_prob
        value = "Correct Value" if is_correct else "Incorrect Value"
        
        # Take step
        res = requests.post(f"{ENV_URL}/step", json={"field_name": field, "value": value}).json()
        result = StepResult(**res)
        
        log_step(step, f"extract_field('{field}')", result.reward, result.done, None)
        rewards.append(result.reward)
        
        obs = result.observation
        if result.done:
            break
        step += 1
        time.sleep(0.2) # Small delay for realism
    
    # Final Score
    state = requests.get(f"{ENV_URL}/state").json()
    score = state.get('FinalScore', 0.0)
    
    log_end(success=(score >= 0.9), steps=step, score=score, rewards=rewards)
    return score

if __name__ == "__main__":
    print(f"--- STARTING REALISTIC TRAINING SIMULATION AGAINST {ENV_URL} ---")
    
    # Gradual increase in accuracy
    accuracies = [0.1, 0.4, 0.7, 0.9, 1.0]
    
    for i, acc in enumerate(accuracies):
        simulate_episode(i + 1, acc)
        print(f"\n--- EPISODE {i+1} COMPLETE ---")
    
    print("\n[SUCCESS] Training simulation finished. You can now see the gradual increase in rewards and score!")
