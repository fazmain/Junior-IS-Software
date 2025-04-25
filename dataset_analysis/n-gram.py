import json
import re
import nltk
import matplotlib.pyplot as plt
from collections import Counter
from nltk.util import ngrams

# Download tokenizer if not already
nltk.download('punkt')

# File path
file_path = "synthetic_daily_chat.jsonl"  # adjust as needed

# Step 1: Load and clean text
all_text = ""
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            content = json.loads(line)["text"]
            cleaned = re.sub(r"<\|turn\|>", "", content)
            cleaned = re.sub(r"<\|startofchat\|>", "", cleaned)
            cleaned = cleaned.replace("’", "'")  # normalize apostrophes
            all_text += cleaned.lower() + " "
        except json.JSONDecodeError:
            continue

# Step 2: Tokenize (preserve contractions)
tokens = nltk.word_tokenize(all_text)
garbage = {"m", "s", "t", "re", "ve", "ll", "d"}
tokens = [word for word in tokens if re.match(r"\w+(?:'\w+)?", word) and word not in garbage]

# Step 3: Count unigrams, bigrams, trigrams
unigram_counts = Counter(tokens)
bigram_counts = Counter(ngrams(tokens, 2))
trigram_counts = Counter(ngrams(tokens, 3))

# Helper function to plot
def plot_ngrams(counter, name, title, n=15):
    items = counter.most_common(n)
    labels = [' '.join(w) if isinstance(w, tuple) else w for w, _ in items]
    values = [count for _, count in items]

    plt.figure(figsize=(10, 5))
    plt.barh(labels[::-1], values[::-1])
    plt.title(f"Top {n} {title}")
    plt.xlabel("Frequency")
    plt.tight_layout()
    plot_name = name
    plt.savefig(plot_name, bbox_inches='tight')
    plt.show()

# Step 4: Visualize
plot_ngrams(unigram_counts, "Unigram", "Unigrams", )
plot_ngrams(bigram_counts, "Bigram", "Bigrams", )
plot_ngrams(trigram_counts, "Trigram", "Trigrams", )
