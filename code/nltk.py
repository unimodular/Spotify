import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
print(nltk.data.path)
nltk.download('all')


# Input and output file paths
input_file = "628_version2_preprocessing_cleaned.csv"
output_file_csv = "628_preprocessing_cleaned_output.csv"
output_file_txt = "628_preprocessing_nltk.txt"

# Read the CSV file
df = pd.read_csv(input_file)

# Ensure 'description' column exists
if 'description' not in df.columns:
    raise ValueError("The 'description' column is missing in the CSV file. Please check the data file!")

# Get NLTK stopwords and add custom stopwords
stop_words = set(stopwords.words('english'))
custom_stop_words = {
    'twitter', 'episode', 'podcast', 'us', 'instagram', 'youtube', 'ad', 'promo', 'visit', 
    'get', 'show', 'use', 'one', 'code', 'first', 'free', 'also', 'today', 'new',
    'learn', 'like', 'week', 'life', 'join', 'see', 'privacy', 'discuss', 'people', 'make', 
    'choices', 'follow', 'podcasts', 'find', 'go', 'listen', 'episodes', 'subscribe'
}
stop_words.update(custom_stop_words)

# Tokenize and extract adjectives/nouns
def preprocess_text(text):
    """
    Tokenize text, remove stopwords, and extract adjectives and nouns.
    """
    if not isinstance(text, str):
        return ""
    
    # Tokenization
    words = word_tokenize(text.lower())
    
    # Filter stopwords and non-alphabetic tokens
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
    
    # POS tagging
    tagged_words = pos_tag(filtered_words)
    
    # Extract adjectives (JJ) and nouns (NN)
    adjective_noun_words = [word for word, tag in tagged_words if tag in ('JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS')]
    
    return " ".join(adjective_noun_words)

# Preprocess descriptions and create a new column
df['cleaned_description'] = df['description'].dropna().apply(preprocess_text)

# Collect all words for frequency analysis
all_words = []
df['cleaned_description'].dropna().apply(lambda x: all_words.extend(x.split()))

# Count word frequencies
word_counts = Counter(all_words)

# Get the top 600 most common words
top_600_words = word_counts.most_common(600)

# Generate output text
output_text = "Top 600 words (adjectives and nouns):\n"
for word, freq in top_600_words:
    output_text += f"{word}: {freq}\n"
print(output_text)

# Save the word frequencies to a TXT file
with open(output_file_txt, "w", encoding="utf-8") as file:
    file.write(output_text)

print(f"Top word rankings have been saved to: {output_file_txt}")

# Save the processed DataFrame to a CSV file
df.to_csv(output_file_csv, index=False, encoding='utf-8')
print(f"Processed data has been saved to: {output_file_csv}")
