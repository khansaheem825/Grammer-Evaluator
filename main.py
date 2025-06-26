import os
import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import time

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ API Key is missing! Set GEMINI_API_KEY in your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

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

MODEL_OPTIONS = {
    "Gemini 1.5 Flash (Fast)": "gemini-1.5-flash",
    "Gemini 1.5 Pro (Balanced)": "gemini-1.5-pro",
    "Gemini 1.0 Pro (Legacy)": "gemini-pro"
}

if 'history' not in st.session_state:
    st.session_state.history = []
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gemini-1.5-flash"
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'feedback_level' not in st.session_state:
    st.session_state.feedback_level = "Detailed"

def evaluate_text(text, model_name, feedback_level):
    prompt = f"""
    You are an AI assistant skilled in grammar correction and structural refinement.
    Analyze the following text based on the 14 rules and provide:
    - A brief summary of errors found.
    - A revised version of the sentence with corrections.
    - A rating from 1-10 based on how well it follows the criteria.

    **Text to Evaluate:**
    "{text}"

    **Evaluation Criteria:**
    {EVALUATION_CRITERIA}

    **Response Format ({feedback_level} feedback):**
    - Overall Rating: X/10
    - Identified Issues: (list of issues)
    - Suggested Improvements: (specific suggestions)
    - Corrected Version: (revised sentence)
    ""
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.append({
            "timestamp": timestamp,
            "original": text,
            "feedback": response.text,
            "model": model_name
        })
        
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error processing request: {e}"

def display_feedback(feedback):
    if "Overall Rating" in feedback:
        rating_part = feedback.split("Overall Rating:")[1].split("\n")[0].strip()
        try:
            rating = float(rating_part.split("/")[0])
            st.metric("Overall Rating", f"{rating}/10")
            

            progress = rating / 10
            color = "red" if rating < 4 else "orange" if rating < 7 else "green"
            st.progress(progress, text=f"Quality Score: {rating:.1f}/10")

            st.markdown(f"""
            <style>
                .stProgress > div > div > div > div {{
                    background-color: {color};
                }}
            </style>
            """, unsafe_allow_html=True)
        except:
            pass
    
    with st.expander("📝 Detailed Feedback", expanded=True):
        st.write(feedback)

def show_history():
    if st.session_state.history:
        st.subheader("📜 Evaluation History")

        history_df = pd.DataFrame(st.session_state.history)
        history_df = history_df.sort_values("timestamp", ascending=False)
        

        for idx, row in history_df.iterrows():
            with st.expander(f"{row['timestamp']} - {row['original'][:50]}..."):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text_area("Original Text", row['original'], height=100, key=f"orig_{idx}")
                with col2:
                    st.caption(f"Model: {row['model'].split('-')[-1].capitalize()}")
                
                if st.button("Show Feedback", key=f"btn_{idx}"):
                    st.text_area("Feedback", row['feedback'], height=200, key=f"fb_{idx}")
    else:
        st.info("No evaluation history yet. Analyze some text to see it here.")


st.set_page_config(
    page_title="Advanced AI Sentence Evaluator", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)


with st.sidebar:
    st.title("⚙️ Settings")
    
  
    st.session_state.selected_model = st.selectbox(
        "Select AI Model",
        options=list(MODEL_OPTIONS.keys()),
        format_func=lambda x: x,
        index=0
    )
    

    st.session_state.feedback_level = st.radio(
        "Feedback Detail Level",
        options=["Concise", "Detailed", "Comprehensive"],
        index=1
    )
    
    st.session_state.dark_mode = st.toggle("Dark Mode", value=False)
    

    st.markdown("---")
    st.caption("Advanced Options")
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max Response Length", 100, 1000, 400, 50)
    
    st.markdown("---")
    st.button("Clear History", on_click=lambda: st.session_state.history.clear())
    st.markdown("---")
    st.caption("ℹ️ About")
    st.caption("This tool evaluates text against 14 linguistic criteria for clarity and effectiveness.")

# Apply dark mode if selected
if st.session_state.dark_mode:
    dark_mode_css = """
    <style>
        :root {
            --primary-color: #9fd3c7;
            --background-color: #0e1117;
            --secondary-background-color: #192841;
            --text-color: #f0f2f6;
            --font: sans-serif;
        }
        .stTextArea textarea {
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
        }
    </style>
    """
    st.markdown(dark_mode_css, unsafe_allow_html=True)


st.title("🔍 Advanced AI Sentence Evaluator")
st.write("Analyze and improve your sentences based on comprehensive linguistic criteria.")

tab1, tab2, tab3 = st.tabs(["📝 Evaluate Text", "📊 Batch Analysis", "📜 History & Reports"])

with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        user_text = st.text_area(
            "✏️ Enter your text below:", 
            placeholder="Type your sentence here...",
            height=200,
            key="main_input"
        )
        
        analyze_col, _, stats_col = st.columns([2, 1, 3])
        with analyze_col:
            if st.button("🚀 Analyze Text", use_container_width=True):
                if user_text.strip():
                    with st.spinner("Analyzing your text..."):
                        feedback = evaluate_text(
                            user_text, 
                            MODEL_OPTIONS[st.session_state.selected_model],
                            st.session_state.feedback_level
                        )
                        st.session_state.last_feedback = feedback
                        st.session_state.last_text = user_text
                        time.sleep(0.5) 
                        st.rerun()
                else:
                    st.warning("⚠️ Please enter text before clicking 'Analyze Text'.")
        
        with stats_col:
            if st.session_state.history:
                last_eval = st.session_state.history[-1]
                st.caption(f"Last evaluated: {last_eval['timestamp']}")
    
    with col2:
        if 'last_feedback' in st.session_state:
            st.subheader("📊 Evaluation Results")
            display_feedback(st.session_state.last_feedback)
        else:
            st.info("💡 Enter some text and click 'Analyze' to see feedback here")
            
      
            with st.expander("💡 Quick Tips for Better Text"):
                st.markdown("""
                - Keep sentences under 20 words
                - Avoid absolute terms like 'always' or 'never'
                - Express one complete thought per sentence
                - Use simple, direct language
                - Eliminate double negatives
                """)

with tab2:
    st.subheader("📚 Batch Text Analysis")
    st.caption("Evaluate multiple sentences at once (one per line)")
    
    batch_text = st.text_area(
        "Enter multiple sentences (one per line):",
        height=300,
        placeholder="Sentence 1\nSentence 2\nSentence 3\n..."
    )
    
    if st.button("Analyze All", key="batch_analyze"):
        if batch_text.strip():
            sentences = [s.strip() for s in batch_text.split('\n') if s.strip()]
            progress_bar = st.progress(0)
            results = []
            
            for i, sentence in enumerate(sentences):
                progress_bar.progress((i + 1) / len(sentences), f"Processing {i+1}/{len(sentences)}")
                feedback = evaluate_text(
                    sentence,
                    MODEL_OPTIONS[st.session_state.selected_model],
                    "Concise"  
                )
                results.append({"Sentence": sentence, "Feedback": feedback})
            
            st.success("✅ Analysis complete!")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("Please enter some text to analyze")

with tab3:
    show_history()
    

    if st.session_state.history:
        st.markdown("---")
        st.subheader("📈 Performance Metrics")
        

        ratings = []
        for item in st.session_state.history:
            if "Overall Rating" in item['feedback']:
                try:
                    rating_part = item['feedback'].split("Overall Rating:")[1].split("\n")[0].strip()
                    rating = float(rating_part.split("/")[0])
                    ratings.append(rating)
                except:
                    continue
        
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Evaluations", len(st.session_state.history))
            col2.metric("Average Rating", f"{avg_rating:.1f}/10")
            col3.metric("Best Rating", f"{max(ratings):.1f}/10")
            
       
            chart_data = pd.DataFrame({
                "Rating": ratings,
                "Count": range(len(ratings))
            })
            st.line_chart(chart_data.set_index("Count")["Rating"])
        else:
            st.info("No rating data available in history")


st.markdown("---")
footer_col1, footer_col2 = st.columns([3, 1])
with footer_col1:
    st.caption("🚀 Developed with Streamlit & Gemini AI | Linguistic Evaluation Tool")
with footer_col2:
    st.caption(f"v1.2 | {datetime.now().year}")
