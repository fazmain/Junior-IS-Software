# Code to measure the inference speed of the model

import time
from llama_cpp import Llama
from huggingface_hub import hf_hub_download


model_path = hf_hub_download(
    repo_id="fazmain/swiftcompose-llama-1b",
    filename="unsloth.Q4_K_M.gguf"  # Replace with your actual filename
)

# Initialize model
llm = Llama(model_path=model_path, n_ctx=512)

# Test prompt
prompt = "Hey, how was your day?"

# Number of tokens to generate
N = 10

# Start timer
start = time.time()

# Run inference
output = llm(
    prompt,
    max_tokens=N,
    temperature=0.4,
    top_p=0.95,
    stop=["\n", "You:"]
)

end = time.time()

# Extract generated text
text = output["choices"][0]["text"].strip()

# Report timings
total_time = end - start
avg_time_per_token = total_time / N

print("=== Inference Benchmark ===")
print(f"Prompt: {prompt}")
print(f"Generated: {text}")
print(f"Total Time: {total_time:.4f} seconds")
print(f"Avg Time per Token: {avg_time_per_token:.4f} seconds")
