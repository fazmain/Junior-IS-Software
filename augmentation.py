import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
import nlpaug.flow as naf
from nlpaug.util import Action
import json
import re
import random


aug = naf.Sequential([
    nac.KeyboardAug()  
])

# Define a function to split text into tokens and non-tokens
# and augment only the non-token parts

def augment_text_excluding_tokens(text, aug, n=1, augment_probability=0.05):
    # Split the text into turns
    turns = text.split("<|turn|>")
    
    # Process each turn
    augmented_turns = []
    for i, turn in enumerate(turns):
        if i == 0:  # Keep the startofchat token as is
            augmented_turns.append(turn)
            continue
            
        # Randomly decide whether to augment this turn
        if random.random() < augment_probability:
            # Augment the turn content
            augmented_text = aug.augment(turn.strip(), n=1)[0]
            augmented_turns.append(augmented_text)
        else:
            # Keep the original turn
            augmented_turns.append(turn)
    
    # Reconstruct the text with <|turn|> tokens
    augmented_text = augmented_turns[0]  # Start with first part (contains startofchat)
    for turn in augmented_turns[1:]:
        augmented_text += "<|turn|>" + turn
    
    return [augmented_text]  # Return as list to maintain compatibility

# Remove the decode_unicode_escapes function and ensure apostrophes are preserved

# Open the input and output files
with open('synthetic_daily_chat.jsonl', 'r') as f, open('augmented_daily_chat.jsonl', 'w') as out_f:
    for line in f:
        data = json.loads(line)
        
        # Apply augmentation to the text field
        if 'text' in data:
            augmented_texts = augment_text_excluding_tokens(data['text'], aug, n=1)
            
            # Write augmented texts to the new file
            for aug_text in augmented_texts:
                new_data = data.copy()
                new_data['text'] = aug_text
                out_f.write(json.dumps(new_data, ensure_ascii=False) + '\n')

            # Print original and augmented texts
            print(f"Original: {data['text']}")
            for i, aug_text in enumerate(augmented_texts):
                print(f"Augmented {i+1}: {aug_text}")
            print("-" * 50)

