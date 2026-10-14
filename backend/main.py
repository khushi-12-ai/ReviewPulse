from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

from nlp_processor import process_reviews
from report_generator import generate_pdf_report, generate_excel_report
from ai_summarizer import generate_summary

app = FastAPI(title="Review Analyzer API")

# Allow CORS for Streamlit/React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store the latest analysis globally (for simplicity in this demo; in production use a DB/cache)
latest_analysis = {}

@app.get("/")
def read_root():
    return {"message": "Review Analyzer API is running"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    text_column: str = Form(...),
    date_column: str = Form(None)
):
    global latest_analysis
    try:
        # Read file with encoding fallback
        contents = await file.read()
        filename_lower = (file.filename or "").lower()
        if filename_lower.endswith(('.csv', '.tsv', '.txt')):
            sep = '\t' if filename_lower.endswith('.tsv') else ','
            df = None
            for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding=enc, sep=sep)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception:
                    continue
            if df is None:
                df = pd.read_csv(io.BytesIO(contents), encoding='latin-1', on_bad_lines='skip')
        elif filename_lower.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported (.csv, .xlsx, .xls)")
            
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Smart text column matching
        resolved_text_col = None
        requested_col = text_column.strip() if text_column else ""
        
        # 1. Exact or case-insensitive match for requested column
        for col in df.columns:
            if col.lower() == requested_col.lower():
                resolved_text_col = col
                break
                
        # 2. Keyword-based matching
        if not resolved_text_col:
            keywords = ['review_text', 'review text', 'review', 'reviews', 'feedback', 'comment', 'comments', 'text', 'content', 'message', 'body', 'description', 'summary', 'opinion']
            for kw in keywords:
                for col in df.columns:
                    c_low = col.lower()
                    if kw in c_low and not any(c_low.endswith(bad) or c_low == bad for bad in ['_id', ' id', 'id', '_num']):
                        resolved_text_col = col
                        break
                if resolved_text_col:
                    break
                    
        # 3. Heuristic: Column with highest average string length
        if not resolved_text_col:
            candidate_cols = []
            for col in df.columns:
                non_nulls = df[col].dropna().astype(str)
                non_nulls = non_nulls[~non_nulls.str.lower().isin(['nan', 'none', 'null', ''])]
                if len(non_nulls) > 0:
                    avg_len = non_nulls.str.len().mean()
                    candidate_cols.append((col, avg_len))
            if candidate_cols:
                candidate_cols.sort(key=lambda x: x[1], reverse=True)
                resolved_text_col = candidate_cols[0][0]
            elif len(df.columns) > 0:
                resolved_text_col = df.columns[0]
            else:
                raise HTTPException(status_code=400, detail="Uploaded file has no readable columns.")
                
        text_column = resolved_text_col
        
        # Smart date column matching
        if date_column and str(date_column).strip().lower() not in ["none", ""]:
            requested_date = str(date_column).strip()
            resolved_date_col = None
            for col in df.columns:
                if col.lower() == requested_date.lower():
                    resolved_date_col = col
                    break
            if not resolved_date_col:
                for kw in ['date', 'time', 'timestamp', 'created', 'posted', 'year', 'day']:
                    for col in df.columns:
                        if kw in col.lower():
                            resolved_date_col = col
                            break
                    if resolved_date_col:
                        break
            date_column = resolved_date_col
        else:
            date_column = None
        
        # Filter out empty or whitespace-only reviews
        df = df[df[text_column].notna()]
        df = df[~df[text_column].astype(str).str.strip().str.lower().isin(['nan', 'none', 'null', ''])]
        
        if len(df) == 0:
            raise HTTPException(status_code=400, detail=f"No valid text entries found in column '{text_column}'.")
        
        # Limit rows for demo performance
        if len(df) > 1000:
            df = df.head(1000)
            
        # 1. NLP Processing
        analysis_results = process_reviews(df, text_column, date_column)
        
        # 2. AI Summary
        ai_summary = generate_summary(df, text_column)
        analysis_results['ai_summary'] = ai_summary
        
        # Store for report generation endpoint
        latest_analysis = analysis_results
        
        # Return JSON-friendly results (without the large processed_df)
        return JSONResponse({
            "message": "Analysis successful",
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
            # We send the full processed data for the Streamlit dashboard
            "processed_data": analysis_results['processed_df'].fillna('').to_dict(orient='records')
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report/pdf")
def get_pdf_report():
    if not latest_analysis:
        raise HTTPException(status_code=404, detail="No analysis found. Upload a file first.")
    
    pdf_buffer = generate_pdf_report(latest_analysis)
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=analysis_report.pdf"}
    )

@app.get("/report/excel")
def get_excel_report():
    if not latest_analysis:
        raise HTTPException(status_code=404, detail="No analysis found. Upload a file first.")
    
    if 'processed_df' not in latest_analysis:
        raise HTTPException(status_code=500, detail="Processed DataFrame missing.")
        
    excel_buffer = generate_excel_report(latest_analysis['processed_df'])
    return StreamingResponse(
        excel_buffer, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=processed_reviews.xlsx"}
    )
