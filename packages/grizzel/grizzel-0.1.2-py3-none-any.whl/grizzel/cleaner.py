import re
import string
import unicodedata
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize tools
lemmatizer = WordNetLemmatizer()
stopword_set = set(stopwords.words('english'))

# Unicode-safe whitespace cleaner
def clean_whitespace(text):
    # Replace all Unicode space characters (category 'Z') with space
    text = ''.join(
        ' ' if unicodedata.category(char).startswith('Z') else char
        for char in text
    )
    # Remove zero-width and invisible characters
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    # Collapse all types of whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Main preprocessing function

def clean_text(text):
    # Convert to lowercase and strip surrounding whitespace
    text = str(text).lower().strip()

    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove numbers
    text = re.sub(r'\d+', ' ', text)

    # Replace multiple periods with a space
    text = re.sub(r'\.{2,}', ' ', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Clean up any strange or extra whitespace before tokenizing
    text = clean_whitespace(text)

    # Tokenize
    tokens = word_tokenize(text)

    # Lemmatize and remove stopwords
    cleaned_tokens = [
        lemmatizer.lemmatize(tok)
        for tok in tokens
        if tok not in stopword_set and tok.strip()
    ]

    # Rejoin and final whitespace cleanup
    cleaned_text = ''.join(cleaned_tokens)
    cleaned_text = clean_whitespace(cleaned_text)

    return cleaned_text  

