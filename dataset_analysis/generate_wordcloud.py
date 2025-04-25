import json
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# File path to your .jsonl file
file_path = "augmented_daily_chat.jsonl"  # Change if needed

# Step 1: Load and clean text
all_text = ""
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            content = json.loads(line)["text"]
            cleaned = re.sub(r"<\|turn\|>", "", content)
            cleaned = re.sub(r"<\|startofchat\|>", "", cleaned)
            cleaned = cleaned.replace("’", "'")  # normalize apostrophes
            all_text += cleaned + " "
        except json.JSONDecodeError:
            continue

# Step 2: Tokenize while preserving contractions like "I'm", "don't"
tokens = re.findall(r"\b\w+(?:'\w+)?\b", all_text.lower())

# Step 3: Filter out garbage tokens like standalone "m", "s"
garbage_words = {"m", "s", "t", "re", "ve", "ll", "d"}  # common contraction fragments
filtered_tokens = [word for word in tokens if word not in garbage_words]

# Step 4: Generate final text and WordCloud
final_text = " ".join(filtered_tokens)

wordcloud = WordCloud(
    width=1000,
    height=500,
    background_color='white',
    collocations=False
).generate(final_text)

# Step 5: Show the word cloud
plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('wordcloud.png', dpi=300, bbox_inches='tight')  
plt.close() 
