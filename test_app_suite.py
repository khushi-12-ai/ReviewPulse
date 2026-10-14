import sys
import os
import io
import pandas as pd

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
WEB_DIR = os.path.join(PROJECT_ROOT, "web")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

def test_nlp_processor():
    print("--- 1. Testing nlp_processor ---")
    from nlp_processor import clean_text, tokenize_and_process, analyze_sentiment, extract_regex_patterns, detect_spam, process_reviews
    
    # Text cleaning
    raw = "<p>Check https://example.com! The battery was amazing, order #ORD-12345.</p>"
    cleaned = clean_text(raw)
    assert "<p>" not in cleaned, "HTML tags not removed"
    assert "https://" not in cleaned, "URL not removed"
    print("  [PASS] clean_text removes HTML and URLs")
    
    # Tokenize and process
    res = tokenize_and_process(cleaned)
    assert "raw_tokens" in res, "Missing raw_tokens"
    assert "stopwords_removed" in res, "Missing stopwords_removed"
    assert "filtered_tokens" in res, "Missing filtered_tokens"
    assert "stems" in res, "Missing stems"
    assert "lemmas" in res, "Missing lemmas"
    assert "pos_tags" in res, "Missing pos_tags"
    assert len(res["raw_tokens"]) > 0, "No raw tokens generated"
    assert "was" in res["stopwords_removed"] or "the" in [w.lower() for w in res["stopwords_removed"]], "Stopwords not correctly identified"
    print(f"  [PASS] tokenize_and_process generated {len(res['raw_tokens'])} raw tokens, {len(res['stopwords_removed'])} stopwords, {len(res['filtered_tokens'])} clean tokens")
    
    # Sentiment
    pos_res = analyze_sentiment("Absolutely amazing, outstanding quality!")
    neg_res = analyze_sentiment("Terrible, awful, broke immediately.")
    assert pos_res["label"] == "Positive", f"Expected Positive, got {pos_res['label']}"
    assert neg_res["label"] == "Negative", f"Expected Negative, got {neg_res['label']}"
    print("  [PASS] analyze_sentiment correctly identified Positive and Negative")
    
    # Regex
    regex_res = extract_regex_patterns("Contact support@shop.com or call +1-800-555-0199 for ORD-99881")
    assert "support@shop.com" in regex_res["emails"], "Email not detected"
    assert "ORD-99881" in regex_res["order_ids"], "Order ID not detected"
    print("  [PASS] extract_regex_patterns extracted emails and order IDs")
    
    # Spam
    is_spam, reason = detect_spam("SPAM", is_duplicate=False)
    assert is_spam, "Short text should be flagged as spam"
    print(f"  [PASS] detect_spam correctly flagged: {reason}")
    
    # Full process_reviews
    sample_df = pd.DataFrame({
        "Review": [
            "Great wireless earbuds, noise cancellation is superb!",
            "Horrible product, stopped working after 2 days. Emailed support@audio.com"
        ],
        "Date": ["2024-01-01", "2024-01-02"]
    })
    analysis = process_reviews(sample_df, "Review", "Date")
    assert "processed_df" in analysis, "processed_df missing"
    assert "stopword_frequency" in analysis, "stopword_frequency missing"
    assert "raw_token_count" in analysis, "raw_token_count missing"
    p_df = analysis["processed_df"]
    assert "Raw_Tokens" in p_df.columns, "Raw_Tokens missing in processed_df"
    assert "Stopwords_Removed" in p_df.columns, "Stopwords_Removed missing in processed_df"
    assert "Stems" in p_df.columns, "Stems missing in processed_df"
    assert "Lemmas" in p_df.columns, "Lemmas missing in processed_df"
    print("  [PASS] process_reviews completed successfully with full NLP columns")

def test_report_generator():
    print("--- 2. Testing report_generator (with Unicode and Emojis) ---")
    from report_generator import generate_pdf_report, generate_excel_report
    
    mock_analysis = {
        "sentiment_distribution": {"Positive": 10, "Neutral": 3, "Negative": 2},
        "keywords": ["sound 🎧", "quality ⭐", "battery", "service"],
        "ngrams": ["great sound", "battery life", "customer support"],
        "top_entities": [("Apple", 5), ("Amazon", 3)],
        "ai_summary": "Customers love the build quality 🚀 and battery life! Main complaint: delayed shipping."
    }
    
    pdf_bytes = generate_pdf_report(mock_analysis)
    assert pdf_bytes is not None and len(pdf_bytes.getvalue()) > 0, "PDF buffer is empty"
    print(f"  [PASS] PDF report generated without UnicodeEncodeError ({len(pdf_bytes.getvalue())} bytes)")
    
    mock_df = pd.DataFrame({
        "Original_Text": ["Great product!", "Bad service."],
        "Tokens": [["great", "product"], ["bad", "service"]],
        "Sentiment": ["Positive", "Negative"]
    })
    excel_bytes = generate_excel_report(mock_df)
    assert excel_bytes is not None and len(excel_bytes.getvalue()) > 0, "Excel buffer is empty"
    print(f"  [PASS] Excel report generated successfully ({len(excel_bytes.getvalue())} bytes)")

def test_analyzer_service():
    print("--- 3. Testing analyzer_service ---")
    import analyzer_service
    
    df = analyzer_service.get_sample_dataset()
    assert len(df) >= 10, "Sample dataset too small"
    
    t_col, d_col = analyzer_service.detect_columns(df)
    assert t_col == "Review_Text", f"Expected Review_Text, got {t_col}"
    assert d_col == "Date", f"Expected Date, got {d_col}"
    print(f"  [PASS] detect_columns detected: text='{t_col}', date='{d_col}'")
    
    # Run analysis local
    res = analyzer_service.run_analysis_local(df, t_col, d_col)
    assert res["engine"] == "local"
    assert len(res["processed_data"]) == len(df)
    assert "stopword_frequency" in res
    print(f"  [PASS] run_analysis_local processed {len(res['processed_data'])} reviews cleanly")

def test_fastapi_backend():
    print("--- 4. Testing FastAPI backend app ---")
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # Root check
    r = client.get("/")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("  [PASS] GET / returned 200")
    
    # Upload test with CSV
    csv_content = "Review Text,Date\nSuper fast shipping and great quality!,2024-01-10\nBroke after 1 hour of use,2024-01-11\n"
    files = {"file": ("test_reviews.csv", csv_content.encode("utf-8"), "text/csv")}
    data = {"text_column": "Review Text", "date_column": "Date"}
    
    upload_resp = client.post("/upload", files=files, data=data)
    assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.status_code} - {upload_resp.text}"
    json_data = upload_resp.json()
    assert "processed_data" in json_data
    assert "sentiment_distribution" in json_data
    assert "stopword_frequency" in json_data
    print(f"  [PASS] POST /upload processed CSV successfully with {len(json_data['processed_data'])} rows")
    
    # Test report endpoints
    pdf_resp = client.get("/report/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    print("  [PASS] GET /report/pdf returned valid PDF stream")
    
    excel_resp = client.get("/report/excel")
    assert excel_resp.status_code == 200
    print("  [PASS] GET /report/excel returned valid Excel stream")

if __name__ == "__main__":
    print("========================================")
    print("RUNNING COMPLETE REVIEW ANALYZER APP TESTS")
    print("========================================")
    test_nlp_processor()
    test_report_generator()
    test_analyzer_service()
    test_fastapi_backend()
    print("========================================")
    print("ALL APP TESTS PASSED SUCCESSFULLY! (100%)")
    print("========================================")
