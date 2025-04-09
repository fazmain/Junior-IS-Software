# autocomplete.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

MAX_CONTEXT_TOKENS = 500
PREDICTION_TOKENS = 10

def get_suggestion(prompt: str):
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_CONTEXT_TOKENS).input_ids.to(device)

    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=PREDICTION_TOKENS,
            do_sample=True,
            temperature=0.4,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )

    full_text = tokenizer.decode(output[0], skip_special_tokens=True)
    generated = " " + full_text[len(prompt):].strip().split("\n")[0]
    return generated
