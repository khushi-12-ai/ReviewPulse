import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import pandas as pd
from langdetect import detect
from deep_translator import GoogleTranslator
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
# Download NLTK resources (will only download if not present)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load Spacy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

analyzer = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove special characters and digits (keep basic punctuation for sentence structure in sentiment)
    text = re.sub(r'[^a-zA-Z\s.,!?]', '', text)
    return text.strip()

def tokenize_and_process(text):
    if not text:
        return {
            "raw_tokens": [],
            "stopwords_removed": [],
            "filtered_tokens": [],
            "tokens": [],
            "stems": [],
            "lemmas": [],
            "cleaned_text": "",
            "pos_tags": [],
            "entities": []
        }
    doc = nlp(text)
    raw_tokens = []
    stopwords_removed = []
    filtered_tokens = []
    stems = []
    lemmas = []
    pos_tags = []
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    for token in doc:
        # Ignore punctuation and spaces
        if not token.is_punct and not token.is_space:
            word_text = token.text
            lower_word = word_text.lower()
            raw_tokens.append(word_text)
            pos_tags.append((word_text, token.pos_))
            
            if lower_word in stop_words:
                stopwords_removed.append(word_text)
            else:
                filtered_tokens.append(word_text)
                stems.append(stemmer.stem(lower_word))
                lemmas.append(token.lemma_.lower() if token.lemma_ else lower_word)
            
    return {
        "raw_tokens": raw_tokens,
        "stopwords_removed": stopwords_removed,
        "filtered_tokens": filtered_tokens,
        "tokens": filtered_tokens,
        "stems": stems,
        "lemmas": lemmas,
        "cleaned_text": " ".join(filtered_tokens),
        "pos_tags": pos_tags,
        "entities": entities
    }

def analyze_sentiment(text):
    if not text:
        return {"compound": 0, "label": "Neutral"}
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    return {"compound": compound, "label": label}

def extract_entities(text):
    if not text:
        return []
    doc = nlp(str(text))
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    return entities

def extract_named_entities(text):
    """Extract named entities with categories from text."""
    return extract_entities(text)

def pos_tag_text(text):
    """Tags tokens in text with parts of speech (POS). Returns list of (word, pos_tag) tuples."""
    if not text:
        return []
    doc = nlp(str(text))
    return [(token.text, token.pos_) for token in doc if not token.is_punct and not token.is_space]

def extract_ngrams(text, n_range=(2, 3), top_n=5):
    """Extracts contiguous n-gram phrases from a text string."""
    if not text or not str(text).strip():
        return []
    try:
        vec = CountVectorizer(ngram_range=n_range, stop_words='english')
        vec.fit([str(text)])
        phrases = vec.get_feature_names_out().tolist()
        if phrases:
            return phrases[:top_n]
    except Exception:
        pass
    # Fallback to simple sliding window if CountVectorizer doesn't yield phrases
    words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{2,}\b', str(text)) if w.lower() not in stop_words]
    res = []
    if len(words) >= 2:
        for i in range(len(words) - 1):
            res.append(f"{words[i]} {words[i+1]}")
    return res[:top_n]

def extract_regex_patterns(text):
    if not isinstance(text, str):
        return {"emails": [], "phones": [], "order_ids": []}
    
    # Very basic regex patterns
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    # Simple phone number (US-centric or generic digits)
    phones = re.findall(r'\+?\d[\d -]{8,12}\d', text)
    # Mock order ID pattern (e.g. #ORD-12345 or 111-1234567-1234567)
    order_ids = re.findall(r'#?ORD-\d+|[0-9]{3}-[0-9]{7}-[0-9]{7}', text)
    
    return {
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "order_ids": list(set(order_ids))
    }

def detect_spam(text, is_duplicate):
    if not isinstance(text, str) or len(text.strip()) == 0:
        return False, "Empty Text"
    
    if is_duplicate:
        return True, "Duplicate Review"
        
    words = text.split()
    if len(words) < 3:
        return True, "Extremely Short"
        
    # Check for excessive repetition (e.g. 'good good good')
    if len(words) >= 3 and len(set(words)) == 1:
        return True, "Spammy Repetition"
        
    # Check for excessive caps
    upper_count = sum(1 for c in text if c.isupper())
    if len(text) > 0 and (upper_count / len(text)) > 0.5:
        return True, "Excessive Caps"
        
    excl_count = text.count('!')
    if len(text) > 0 and (excl_count / len(text)) > 0.2:
        return True, "Excessive Punctuation"
        
    return False, "Genuine"

_translation_cache = {}

def process_reviews(df, text_column, date_column=None):
    """
    Processes a whole dataframe column of reviews and returns a rich set of analysis.
    """
    global _translation_cache
    if len(df) > 300:
        df = df.head(300)

    processed_data = []
    all_tokens = []
    all_raw_tokens = []
    all_stopwords = []
    all_entities = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    # Identify duplicates in advance
    duplicates = set(df[df.duplicated(subset=[text_column], keep=False)][text_column].dropna().astype(str))
    all_texts_for_topics = []
    translations_done = 0
    
    for idx, row in df.iterrows():
        raw_text = str(row.get(text_column, '')).strip()
        if not raw_text:
            continue
        
        # Get Date if available
        review_date = str(row.get(date_column, '')) if date_column and date_column in df.columns else ""
        
        # 1. Fake/Spam Detection
        is_dup = raw_text in duplicates
        is_spam, spam_reason = detect_spam(raw_text, is_dup)
        
        # 2. Fast Multilingual Translation
        is_pure_ascii = all(ord(c) < 128 for c in raw_text)
        if is_pure_ascii:
            original_language = "en"
            translated_text = raw_text
        else:
            try:
                lang = detect(raw_text)
            except Exception:
                lang = "unknown"
            original_language = lang
            translated_text = raw_text
            
            if lang not in ["en", "unknown"] and len(raw_text) > 3:
                if raw_text in _translation_cache:
                    translated_text = _translation_cache[raw_text]
                elif translations_done < 10:
                    try:
                        translated_text = GoogleTranslator(source='auto', target='en').translate(raw_text[:400])
                        _translation_cache[raw_text] = translated_text
                        translations_done += 1
                    except Exception:
                        translated_text = raw_text
        
        # Regex extractions (on translated text)
        regex_data = extract_regex_patterns(translated_text)
        
        # Clean text for NLP
        cleaned = clean_text(translated_text)
        
        # Tokenize, Stopwords, Lemma, Stem, POS, Entities (single-pass)
        nlp_data = tokenize_and_process(cleaned)
        all_tokens.extend(nlp_data['tokens'])
        all_raw_tokens.extend(nlp_data['raw_tokens'])
        all_stopwords.extend(nlp_data['stopwords_removed'])
        
        # Sentiment
        sentiment = analyze_sentiment(translated_text)
        sentiment_counts[sentiment["label"]] += 1
        
        # Entities
        entities = nlp_data.get('entities', [])
        for e in entities:
            all_entities.append(f"{e['text']} ({e['label']})")
            
        processed_data.append({
            "Original_Text": raw_text,
            "Date": review_date,
            "Original_Language": original_language,
            "Translated_Text": translated_text,
            "Is_Spam": is_spam,
            "Spam_Reason": spam_reason,
            "Cleaned_Text": nlp_data["cleaned_text"],
            "Raw_Tokens": nlp_data["raw_tokens"],
            "Stopwords_Removed": nlp_data["stopwords_removed"],
            "Tokens": nlp_data["tokens"],
            "Stems": nlp_data["stems"],
            "Lemmas": nlp_data["lemmas"],
            "POS_Tags": nlp_data["pos_tags"],
            "Sentiment_Label": sentiment["label"],
            "Sentiment_Score": sentiment["compound"],
            "Entities": entities,
            "Emails": regex_data["emails"],
            "Phones": regex_data["phones"],
            "Order_IDs": regex_data["order_ids"],
        })
        
        # Only add valid texts for topic modeling
        if len(translated_text.split()) >= 3 and not is_spam:
            all_texts_for_topics.append(translated_text)

    # Calculate Topic Modeling using LDA (scikit-learn)
    topics_data = []
    try:
        if len(all_texts_for_topics) >= 5: # Need a minimum number of documents
            vectorizer = CountVectorizer(stop_words='english', max_features=1000)
            doc_term_matrix = vectorizer.fit_transform(all_texts_for_topics)
            
            num_topics = min(5, max(2, len(all_texts_for_topics) // 10))
            lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
            lda_model.fit(doc_term_matrix)
            
            feature_names = vectorizer.get_feature_names_out()
            
            # Count dominant topic per document to get topic size
            doc_topic_dist = lda_model.transform(doc_term_matrix)
            dominant_topics = doc_topic_dist.argmax(axis=1)
            topic_counts = pd.Series(dominant_topics).value_counts().to_dict()
            
            for topic_idx, topic in enumerate(lda_model.components_):
                top_word_indices = topic.argsort()[-5:][::-1]
                top_words = [feature_names[i] for i in top_word_indices]
                topic_size = topic_counts.get(topic_idx, 0)
                
                # Create a pseudo-name for the topic
                topic_name = " / ".join(top_words[:3]).title()
                
                topics_data.append({
                    "Topic_ID": topic_idx + 1,
                    "Count": topic_size,
                    "Name": topic_name,
                    "Top_Words": top_words
                })
    except Exception as e:
        print(f"LDA Topic Modeling Error: {e}")

    # Calculate overall frequencies and TF-IDF
    tfidf = TfidfVectorizer(max_features=20, ngram_range=(1, 2))
    
    # Word Frequency
    word_freq = Counter(all_tokens).most_common(50)
    
    # Entity Frequency
    top_entities = Counter(all_entities).most_common(30)
    
    # N-grams (Bigrams and Trigrams)
    try:
        tfidf = TfidfVectorizer(ngram_range=(2,3), stop_words='english', max_features=30)
        tfidf_matrix = tfidf.fit_transform(pd.DataFrame(processed_data)['Cleaned_Text'].fillna(''))
        top_ngrams = tfidf.get_feature_names_out().tolist()
    except Exception as e:
        top_ngrams = []
        
    # TF-IDF Keywords (Unigrams)
    try:
        tfidf_uni = TfidfVectorizer(stop_words='english', max_features=30)
        tfidf_uni.fit_transform(pd.DataFrame(processed_data)['Cleaned_Text'].fillna(''))
        top_keywords = tfidf_uni.get_feature_names_out().tolist()
    except Exception:
        top_keywords = []
        
    # Stopword Frequency
    stopword_freq = Counter(all_stopwords).most_common(50)
        
    return {
        "processed_df": pd.DataFrame(processed_data),
        "word_frequency": word_freq,
        "stopword_frequency": stopword_freq,
        "raw_token_count": len(all_raw_tokens),
        "stopword_count": len(all_stopwords),
        "sentiment_distribution": sentiment_counts,
        "top_entities": top_entities,
        "ngrams": top_ngrams,
        "keywords": top_keywords,
        "topics": topics_data
    }
