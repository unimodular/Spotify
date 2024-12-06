import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re


keywords_file = "words_BTM.txt"
description_file = "628_preprocessing_cleaned_output.csv"


print("Loading keyword file...")
with open(keywords_file, "r", encoding="utf-8") as file:
    keywords = [line.strip() for line in file.readlines()]
print(f"Loaded {len(keywords)} keywords: {keywords[:10]}")


print("Loading description file...")
descriptions_df = pd.read_csv(description_file)
if 'cleaned_description' not in descriptions_df.columns:
    raise ValueError("The 'cleaned_description' column is missing in the file!")


descriptions = descriptions_df['cleaned_description'].fillna("").tolist()
print(f"Number of descriptions: {len(descriptions)}")


print("Counting keyword frequencies...")
keyword_counts = Counter()

for description in descriptions:
    words = re.findall(r'\b\w+\b', description.lower())
    for keyword in keywords:
        keyword_counts[keyword] += words.count(keyword)


print("Top 10 keyword frequencies:")
for word, count in keyword_counts.most_common(10):
    print(f"{word}: {count}")


print("Generating word cloud...")
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color="white",
    colormap="viridis",
    max_words=200
).generate_from_frequencies(keyword_counts)


plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud from Keyword Frequencies", fontsize=16)
plt.show()
