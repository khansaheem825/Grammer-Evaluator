import os
import streamlit as st
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ API Key is missing! Set GEMINI_API_KEY in your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

# Evaluation Criteria
EVALUATION_CRITERIA = """
Evaluate the given text based on these 14 rules:
1. Avoid statements referring to the past instead of the present.
2. Avoid factual statements or those that could be interpreted as such.
3. Avoid ambiguity and ensure clarity in meaning.
4. Ensure relevance to the intended topic or psychological object.
5. Avoid statements that would be universally accepted or rejected.
6. Cover the full range of the effective scale of interest.
7. Use simple, clear, and direct language.
8. Keep statements short (preferably under 20 words).
9. Each statement should express only one complete thought.
10. Avoid universal terms such as all, always, none, and never.
11. Use words like only, just, merely with caution.
12. Prefer simple sentences over complex or compound ones.
13. Avoid jargon or words that may confuse the target audience.
14. Eliminate double negatives.
"""


#  Function to Evaluate and Correct Text
def evaluate_text(text):
    prompt = f"""
    You are an AI assistant skilled in grammar correction and structural refinement.
    Analyze the following text based on the 14 rules and provide:
    - A brief summary of errors found.
    - A revised version of the sentence with corrections.

    **Text to Evaluate:**
    "{text}"

    **Evaluation Criteria:**
    {EVALUATION_CRITERIA}

    **Expected Response:**
    - Identified issues (if any).
    - Corrected sentence.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ More advanced model
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"⚠️ Error processing request: {e}"


#  Streamlit UI
st.set_page_config(page_title="AI Sentence Evaluator", page_icon="📝", layout="centered")

st.title("🔍 AI Sentence Evaluator")
st.write("Analyze and improve your sentences based on grammar and structure rules.")

# User Input
user_text = st.text_area("✏️ Enter your text below:", placeholder="Type your sentence here...")

if st.button("Analyze Text"):
    if user_text.strip():
        feedback = evaluate_text(user_text)
        st.subheader("✅ Feedback & Suggestions:")
        st.write(feedback)
    else:
        st.warning("⚠️ Please enter text before clicking 'Analyze Text'.")

st.markdown("---")
st.write("🚀 Developed with ❤️ using Streamlit & Gemini AI.")
