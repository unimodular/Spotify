import pandas as pd
import re

def clean_text(text):
    """
    Clean text by removing URLs, email addresses, social media handles, and emojis.
    """
    if not isinstance(text, str):
        return text
    text = re.sub(r"http[s]?://\S+|www\.\S+", "", text)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", text)
    text = re.sub(r"@\w+", "", text)
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F700-\U0001F77F"
        u"\U0001F780-\U0001F7FF"
        u"\U0001F800-\U0001F8FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub(r"", text)
    return text

def contains_non_english(text):
    """
    Check if the text contains non-English characters.
    """
    if not isinstance(text, str):
        return False
    return bool(re.search(r"[^\x00-\x7F]", text))

def clean_abnormal_line_terminators(text):
    """
    Clean abnormal line terminators such as LS and PS.
    """
    if not isinstance(text, str):
        return text
    text = text.replace("\u2028", "").replace("\u2029", "")
    return text

def process_csv(input_file, output_file, non_english_output):
    """
    Process the input CSV file by cleaning the text, removing abnormal line terminators,
    and identifying rows containing non-English characters.
    """
    try:
        print(f"Loading file: {input_file}")
        df = pd.read_csv(input_file, encoding="utf-8")
        print("Cleaning text and removing abnormal line terminators...")
        for col in df.columns:
            df[col] = df[col].apply(clean_text).apply(clean_abnormal_line_terminators)
        
        print("Checking for rows with non-English characters...")
        non_english_rows = df[df.apply(lambda row: any(contains_non_english(str(cell)) for cell in row), axis=1)]
        with open(non_english_output, "w", encoding="utf-8") as file:
            file.write("Rows with non-English characters:\n\n")
            file.write(non_english_rows.to_string(index=False))
        
        print("Saving cleaned data to CSV...")
        df.to_csv(output_file, index=False, encoding="utf-8")
        
        print("Standardizing line endings...")
        with open(output_file, "r", encoding="utf-8") as file:
            content = file.read()
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(content)
        
        print(f"Processing completed. Cleaned data saved to: {output_file}")
        print(f"Rows with non-English characters saved to: {non_english_output}")
    
    except Exception as e:
        print(f"Error processing file: {e}")

def count_episodes_by_keyword(input_file):
    """
    Count the number of episodes for each keyword in the CSV file.
    """
    try:
        df = pd.read_csv(input_file)
        if 'keyword' not in df.columns:
            print("The 'keyword' column is missing in the CSV file.")
            return
        keyword_counts = df['keyword'].value_counts()
        print("Number of episodes per keyword:")
        print(keyword_counts)
    except FileNotFoundError:
        print(f"File {input_file} not found.")
    except Exception as e:
        print(f"Error counting episodes: {e}")

# File paths
input_file = "628_version2.csv"
output_file = "628_version2_preprocessing_cleaned.csv"
non_english_output = "non_english_rows.txt"

# Process CSV file
process_csv(input_file, output_file, non_english_output)

# Count episodes by keyword
count_episodes_by_keyword(output_file)
