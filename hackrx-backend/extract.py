import spacy

# Load the spaCy English model (you may need to install it first: python -m spacy download en_core_web_sm)
nlp = spacy.load('en_core_web_sm')

# Sample sentence
sentence = "The team of doctors were working to improve the health conditions of patients at Bajaj Allianz."

# List of common collective nouns (can be expanded)
collective_nouns = ["team", "group", "committee", "family", "crew", "class", "jury", "audience", "staff", "company"]

def categorize_keywords(sentence):
    # Analyze the sentence using spaCy
    doc = nlp(sentence)
    
    # Initialize dictionaries to store categorized keywords
    keywords = {
        "nouns": [],
        "verbs": [],
        "collective_nouns": []
    }
    
    # Iterate over each token (word) in the sentence
    for token in doc:
        # Categorize based on POS tags
        if token.pos_ == "NOUN":
            if token.text in collective_nouns:
                keywords["collective_nouns"].append(token.text)
            else:
                keywords["nouns"].append(token.text)
        elif token.pos_ == "VERB":
            keywords["verbs"].append(token.text)
    
    return keywords

# Run the function on the sentence
result = categorize_keywords(sentence)

# Print the categorized keywords
print("Categorized Keywords:")
print(f"Nouns: {result['nouns']}")
print(f"Verbs: {result['verbs']}")
print(f"Collective Nouns: {result['collective_nouns']}")
