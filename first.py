import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


MODEL_NAME = "gpt2"  # A small model for quick local testing
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)


text_generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1
)


MAX_CONTEXT_TOKENS = 50
PREDICTION_TOKENS = 5       

def suggest_next_words(user_text, history):

    if not user_text.strip():
        return "", history

    input_ids = tokenizer(user_text, return_tensors="pt", add_special_tokens=False).input_ids
    if input_ids.shape[1] > MAX_CONTEXT_TOKENS:
        input_ids = input_ids[:, -MAX_CONTEXT_TOKENS:]  # keep only the last N tokens

    input_ids = input_ids.to(device)


    output_ids = model.generate(
        input_ids,
        max_new_tokens=PREDICTION_TOKENS,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7
    )


    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    # Isolating the new words from the original text
    # Counting how many tokens in the original prompt
    original_len = input_ids.shape[1]
    # Re-tokenizing the entire output, then splitting off the last few tokens
    full_tokens = tokenizer.encode(generated_text, add_special_tokens=False)
    new_tokens = full_tokens[original_len:]
    suggestion = tokenizer.decode(new_tokens, skip_special_tokens=True)

    # Cleaning up whitespace
    suggestion = suggestion.strip()

    return suggestion, history

def accept_suggestion(user_text, suggestion, history):

    if suggestion:
        if not user_text.endswith((" ", "\n")):
            user_text += " "
        user_text += suggestion
    return user_text, history



with gr.Blocks() as demo:
    gr.Markdown("# Smart Compose Prototype\nType in the textbox, and get a next-word suggestion.")

    with gr.Row():
        note_editor = gr.Textbox(
            label="Your Notes",
            placeholder="Start typing your text here...",
            lines=4,
            # live=True
        )
        suggestion_box = gr.Textbox(
            label="Suggestion",
            interactive=False,
            placeholder="Predicted next words...",
        )


    state = gr.State([])

    accept_button = gr.Button("Accept Suggestion")
    clear_button = gr.Button("Clear All")


    def update_suggestion(user_text, history):
        sug, new_hist = suggest_next_words(user_text, history)
        return sug, new_hist

    note_editor.change(
        fn=update_suggestion,
        inputs=[note_editor, state],
        outputs=[suggestion_box, state]
    )

    def accept_and_update_text(user_text, suggestion, history):
        updated_text, new_hist = accept_suggestion(user_text, suggestion, history)
        new_sug, new_hist = suggest_next_words(updated_text, new_hist)
        return updated_text, new_sug, new_hist

    accept_button.click(
        fn=accept_and_update_text,
        inputs=[note_editor, suggestion_box, state],
        outputs=[note_editor, suggestion_box, state]
    )

    def clear_all():
        return "", "", []

    clear_button.click(
        fn=clear_all,
        inputs=[],
        outputs=[note_editor, suggestion_box, state]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)