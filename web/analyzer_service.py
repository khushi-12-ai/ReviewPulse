import sys
import os
import io
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8000"

# Add backend directory to sys.path for direct local engine fallback
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from nlp_processor import process_reviews
    from ai_summarizer import generate_summary
    from report_generator import generate_pdf_report, generate_excel_report
    LOCAL_ENGINE_AVAILABLE = True
except Exception as e:
    LOCAL_ENGINE_AVAILABLE = False
    logger.warning(f"Local NLP engine not directly importable: {e}")


def is_backend_online(timeout=1.0):
    """Check if the FastAPI backend is running and responding."""
    try:
        r = requests.get(f"{API_URL}/", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def read_file_into_df(file_bytes, filename):
    """Safely reads CSV or Excel file bytes into a pandas DataFrame with encoding fallbacks."""
    name_lower = (filename or "").lower()
    if name_lower.endswith(('.csv', '.tsv', '.txt')):
        sep = '\t' if name_lower.endswith('.tsv') else ','
        for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep=sep)
                df.columns = [str(c).strip() for c in df.columns]
                return df
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                continue
        # Fallback
        df = pd.read_csv(io.BytesIO(file_bytes), encoding='latin-1', on_bad_lines='skip')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    elif name_lower.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(file_bytes))
        df.columns = [str(c).strip() for c in df.columns]
        return df
    else:
        raise ValueError("Unsupported file format. Please upload a .csv, .xlsx, or .xls file.")


def detect_columns(df):
    """Detects likely review text column and optional date column from a DataFrame."""
    cols = list(df.columns)
    if not cols:
        return None, None

    # Priority matches for text columns (full exact or clean match first)
    priority_exact = ['review_text', 'review text', 'review', 'reviews', 'text', 'comment', 'comments', 'feedback', 'review_content', 'content', 'message', 'body', 'description']
    
    text_col = None
    # 1. Exact match
    for p in priority_exact:
        for c in cols:
            c_low = str(c).lower().strip()
            if c_low == p:
                text_col = c
                break
        if text_col:
            break
            
    # 2. Substring match, avoiding _id or id columns like Review_ID
    if not text_col:
        for p in priority_exact:
            for c in cols:
                c_low = str(c).lower().strip()
                if p in c_low and not any(c_low.endswith(bad) or c_low == bad for bad in ['_id', ' id', 'id', '_num']):
                    text_col = c
                    break
            if text_col:
                break

    # 3. Fallback: Column with highest average string length
    if not text_col:
        candidate_cols = []
        for c in cols:
            c_low = str(c).lower().strip()
            if any(c_low.endswith(bad) for bad in ['_id', ' id', 'id']):
                continue
            sample_lens = df[c].dropna().astype(str).str.len()
            if len(sample_lens) > 0:
                candidate_cols.append((c, sample_lens.mean()))
        if candidate_cols:
            candidate_cols.sort(key=lambda x: x[1], reverse=True)
            text_col = candidate_cols[0][0]
        else:
            text_col = cols[0]

    # Date detection: prioritize exact date matches
    date_col = None
    date_candidates = ['date', 'review_date', 'posted_date', 'created_at', 'timestamp', 'time']
    for kw in date_candidates:
        for c in cols:
            c_low = str(c).lower().strip()
            if c_low == kw or c_low.startswith(kw) or c_low.endswith(kw):
                date_col = c
                break
        if date_col:
            break

    return text_col, date_col


def run_analysis_local(df, text_col, date_col=None):
    """Runs NLP processing and summary generation directly in-process."""
    if not LOCAL_ENGINE_AVAILABLE:
        raise RuntimeError("Local NLP engine is not available. Please install backend requirements or start backend server.")

    # Clean df
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    # Filter valid text
    df = df[df[text_col].notna()]
    df = df[~df[text_col].astype(str).str.strip().str.lower().isin(['nan', 'none', 'null', ''])]

    if len(df) == 0:
        raise ValueError(f"No valid text entries found in column '{text_col}'.")

    if len(df) > 1000:
        df = df.head(1000)

    analysis_results = process_reviews(df, text_col, date_col)
    ai_summary = generate_summary(df, text_col)
    analysis_results['ai_summary'] = ai_summary

    processed_records = analysis_results['processed_df'].fillna('').to_dict(orient='records')

    return {
        "message": "Analysis successful (Local Engine)",
        "engine": "local",
        "sentiment_distribution": analysis_results['sentiment_distribution'],
        "word_frequency": analysis_results['word_frequency'],
        "stopword_frequency": analysis_results.get('stopword_frequency', []),
        "raw_token_count": analysis_results.get('raw_token_count', 0),
        "stopword_count": analysis_results.get('stopword_count', 0),
        "top_entities": analysis_results['top_entities'],
        "ngrams": analysis_results['ngrams'],
        "keywords": analysis_results['keywords'],
        "topics": analysis_results.get('topics', []),
        "ai_summary": analysis_results['ai_summary'],
        "processed_data": processed_records
    }


def run_analysis(file_bytes, filename, text_col, date_col=None):
    """
    Attempts to call the FastAPI backend. If the backend is unreachable or fails,
    seamlessly falls back to local Python NLP engine.
    """
    # 1. First, check if backend is online and try it
    backend_ok = is_backend_online(timeout=1.5)
    if backend_ok:
        try:
            files = {"file": (filename, file_bytes, "multipart/form-data")}
            data = {"text_column": text_col, "date_column": date_col or ""}
            response = requests.post(f"{API_URL}/upload", files=files, data=data, timeout=15)
            if response.status_code == 200:
                res = response.json()
                res["engine"] = "api"
                return res
        except Exception as e:
            logger.warning(f"Backend call failed, switching to local engine: {e}")

    # 2. Fallback to local engine
    df = read_file_into_df(file_bytes, filename)
    return run_analysis_local(df, text_col, date_col)


def get_sample_dataset():
    """Returns the comprehensive master review dataset containing dirty data, regex patterns, entities, and languages."""
    csv_candidates = [
        os.path.join(os.path.dirname(__file__), "dirty_reviews_master_dataset.csv"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "dirty_reviews_master_dataset.csv"),
        r"c:\Users\hp\Downloads\ReviewAnalyzerProject\dirty_reviews_master_dataset.csv"
    ]
    for p in csv_candidates:
        if os.path.exists(p):
            try:
                return pd.read_csv(p, encoding='utf-8-sig')
            except Exception:
                pass
    sample_data = [
        {
            "Review_ID": 101,
            "Date": "2024-01-15",
            "Customer_Name": "Sarah Jenkins",
            "Rating": 5,
            "Review_Text": "The wireless headphones are phenomenal! Battery lasts over 30 hours, noise cancelling is top tier, and setup with my iPhone was seamless. Order ORD-84920 delivered right on time.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 102,
            "Date": "2024-01-18",
            "Customer_Name": "Michael Chang",
            "Rating": 1,
            "Review_Text": "Terrible customer service and broken screen upon arrival! I emailed support@soundtech.com twice and called +1-800-555-0199 but got zero response. Avoid this seller. Order ORD-99124.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 103,
            "Date": "2024-01-22",
            "Customer_Name": "Elena Rostova",
            "Rating": 4,
            "Review_Text": "The sound quality and bass are rich and deep. Great build quality from Apple standards, though the charging cable could be a bit longer.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 104,
            "Date": "2024-02-05",
            "Customer_Name": "David Smith",
            "Rating": 3,
            "Review_Text": "Decent product for the price. Works okay for daily conference calls, but ear cushions feel a bit warm after 2 hours of continuous wear.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 105,
            "Date": "2024-02-14",
            "Customer_Name": "Carlos Mendoza",
            "Rating": 5,
            "Review_Text": "¡Excelente producto! La cancelación de ruido es impresionante y la batería dura días. Muy satisfecho con la compra en Amazon.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 106,
            "Date": "2024-02-20",
            "Customer_Name": "Anonymous User",
            "Rating": 1,
            "Review_Text": "SPAM SPAM SPAM buy cheap sunglasses at discountdeals.net",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 107,
            "Date": "2024-02-28",
            "Customer_Name": "Claire Dupont",
            "Rating": 5,
            "Review_Text": "Très bon casque audio, le son est cristallin et le design élégant. Livraison très rapide en France.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 108,
            "Date": "2024-03-02",
            "Customer_Name": "Alex Turner",
            "Rating": 2,
            "Review_Text": "Bluetooth connection keeps dropping every 15 minutes on Windows 11. Very frustrating during zoom meetings. Need a firmware update urgently.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 109,
            "Date": "2024-03-10",
            "Customer_Name": "Jessica Taylor",
            "Rating": 5,
            "Review_Text": "Super comfortable headband and crystal clear microphone! My coworkers in Chicago noticed an instant upgrade in audio quality. Order #ORD-33104.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 110,
            "Date": "2024-03-15",
            "Customer_Name": "Robert Wilson",
            "Rating": 1,
            "Review_Text": "DO NOT BUY! Total scam, stopped working after 3 days. HORRIBLE quality!",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 111,
            "Date": "2024-03-22",
            "Customer_Name": "Anna Mueller",
            "Rating": 4,
            "Review_Text": "Sehr gute Kopfhörer mit fantastischem Klang. Schneller Versand durch DHL nach Berlin. Sehr zufrieden.",
            "Product": "AcousticPro Max"
        },
        {
            "Review_ID": 112,
            "Date": "2024-04-05",
            "Customer_Name": "Kevin Patel",
            "Rating": 5,
            "Review_Text": "Best purchase of 2024! Sleek design, fast USB-C charging, and durable carrying case. Highly recommended to anyone traveling frequently.",
            "Product": "AcousticPro Max"
        }
    ]
    return pd.DataFrame(sample_data)


def detect_and_translate(text: str):
    """Detects review language and translates to English with fallback."""
    from multilingual import detect_and_translate as _dt
    return _dt(text)


def pos_tag_text(text: str):
    """Tags tokens in text with parts of speech (POS)."""
    from nlp_processor import pos_tag_text as _ptt
    return _ptt(text)


def extract_named_entities(text: str):
    """Extracts named entities from text."""
    from nlp_processor import extract_named_entities as _ene
    return _ene(text)


def extract_ngrams(text: str, n_range=(2, 3), top_n=5):
    """Extracts n-gram phrases from text."""
    from nlp_processor import extract_ngrams as _en
    return _en(text, n_range=n_range, top_n=top_n)


