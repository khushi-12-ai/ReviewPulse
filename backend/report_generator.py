import pandas as pd
from fpdf import FPDF
import io

def generate_excel_report(df, filename="report.xlsx"):
    """
    Generates an Excel report from the processed dataframe.
    Returns a BytesIO object with the Excel file content.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Processed_Reviews')
    output.seek(0)
    return output

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Customer Feedback & Review Analyzer Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def _sanitize_pdf_text(val):
    if val is None:
        return ""
    # FPDF uses latin-1 by default; replace incompatible characters
    return str(val).encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(analysis_results, filename="report.pdf"):
    """
    Generates a PDF report containing summary charts and metrics.
    Returns a BytesIO object with the PDF file content.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Summary Metrics
    sentiment_dist = analysis_results.get('sentiment_distribution', {})
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Sentiment Distribution", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Positive Reviews: {sentiment_dist.get('Positive', 0)}", ln=True)
    pdf.cell(0, 10, f"Neutral Reviews: {sentiment_dist.get('Neutral', 0)}", ln=True)
    pdf.cell(0, 10, f"Negative Reviews: {sentiment_dist.get('Negative', 0)}", ln=True)
    pdf.ln(5)
    
    # Top Keywords
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Top Keywords (TF-IDF)", ln=True)
    pdf.set_font("Arial", size=10)
    keywords = ", ".join([_sanitize_pdf_text(k) for k in analysis_results.get('keywords', [])[:15]])
    pdf.multi_cell(0, 10, keywords if keywords else "None extracted")
    pdf.ln(5)
    
    # Common Phrases (N-grams)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. Common Phrases (N-grams)", ln=True)
    pdf.set_font("Arial", size=10)
    ngrams = ", ".join([_sanitize_pdf_text(n) for n in analysis_results.get('ngrams', [])[:15]])
    pdf.multi_cell(0, 10, ngrams if ngrams else "None extracted")
    pdf.ln(5)
    
    # Top Entities
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "4. Top Mentioned Entities", ln=True)
    pdf.set_font("Arial", size=10)
    entities = analysis_results.get('top_entities', [])
    if entities:
        for item in entities[:10]:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                entity, count = item
                pdf.cell(0, 8, _sanitize_pdf_text(f"{entity}: {count} mentions"), ln=True)
    else:
        pdf.cell(0, 8, "None detected", ln=True)
    pdf.ln(5)
    
    # AI Summary if exists
    if 'ai_summary' in analysis_results and analysis_results['ai_summary']:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "5. AI Generated Summary", ln=True)
        pdf.set_font("Arial", size=10)
        text = _sanitize_pdf_text(analysis_results['ai_summary'])
        pdf.multi_cell(0, 8, text)
        
    output = io.BytesIO()
    # fpdf2 allows outputing directly to bytearray via `dest='S'`
    try:
        res = pdf.output(dest='S')
        if isinstance(res, str):
             output.write(res.encode('latin-1'))
        else:
             output.write(res)
    except Exception:
        # Fallback for older fpdf versions
        val = pdf.output(dest='S')
        output.write(val.encode('latin-1'))
    output.seek(0)
    return output
