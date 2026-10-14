import os
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

def generate_summary(df, text_column):
    """
    Generates an AI summary of the reviews using Google Gemini API.
    Highlights main customer complaints and praised features.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Returning a mock summary.")
        return """
**Mock AI Summary (No API Key Provided)**

**Praised Features:**
- Users generally love the battery life and the build quality of the product.
- Customer service is frequently mentioned as responsive and helpful.
- The interface is described as intuitive and user-friendly.

**Main Complaints:**
- Several users complained about delayed shipping and packaging issues.
- The software occasionally crashes during heavy workload.
- Price is considered slightly high compared to competitors.

*(Note: Set the GEMINI_API_KEY environment variable for real AI generation)*
"""

    genai.configure(api_key=api_key)
    # Using the recommended model for text tasks
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # We can't send thousands of reviews to the prompt due to context limits.
    # So we'll sample up to 100 reviews.
    sample_reviews = df[text_column].dropna().sample(n=min(100, len(df))).tolist()
    
    prompt = f"""
    You are an expert customer feedback analyst. 
    Below is a sample of customer reviews for a product/service.
    
    Please read through them and provide a concise summary that highlights:
    1. The main customer complaints (what needs improvement).
    2. The most praised features (what is working well).
    3. An overall conclusion.
    
    Format the output nicely using Markdown with clear headings and bullet points.
    
    Reviews:
    {sample_reviews}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating AI summary: {e}")
        return f"Error generating summary: {str(e)}"
