from llama_cpp import Llama
from huggingface_hub import hf_hub_download

# Download model from Hugging Face
model_path = hf_hub_download(
    repo_id="fazmain/swiftcompose-llama-1b",
    filename="unsloth.Q4_K_M.gguf"  # Replace with your actual filename
)

# Testing another model as base case
# model_path = hf_hub_download(
#     repo_id="DevQuasar/unsloth.Llama-3.2-1B-GGUF",
#     filename="unsloth.Llama-3.2-1B.Q4_K_M.gguf"  # Replace with your actual filename
# )

llm = Llama(model_path=model_path, n_ctx=512)

def get_suggestion(prompt: str):
    output = llm(
        prompt,
        max_tokens=10,
        temperature=0.7,
        top_p=0.95,
        stop=["\n", "You:"]
    )
    return " " + output["choices"][0]["text"].strip()
