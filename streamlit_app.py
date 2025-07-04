import streamlit as st
import requests
import re

st.title('Fake News Detector')
st.write('Enter a news snippet below. Each sentence will be analyzed individually.')

user_input = st.text_area('News Snippet', height=200)

if st.button('Analyze'):
    if not user_input.strip():
        st.warning('Please enter some text to analyze.')
    else:
        # Split input into sentences (simple split, can be improved)
        sentences = re.split(r'(?<=[.!?])\s+', user_input.strip())
        sentences = [s for s in sentences if s.strip()]
        payload = {"paragraphs": [{"text": s} for s in sentences]}
        try:
            response = requests.post(
                'https://fnd-service.onrender.com/analyze',
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                st.subheader('Analysis Results:')
                for idx, result in enumerate(data.get('paragraphs', [])):
                    st.markdown(f"**Sentence {idx+1}:** {sentences[idx]}")
                    label = result.get('label', 'UNKNOWN')
                    conf = result.get('confidence_score', 0)
                    color = 'green' if label == 'REAL' else ('red' if label == 'FAKE' else 'orange')
                    label_text = 'Likely True' if label == 'REAL' else ('Likely Fake' if label == 'FAKE' else 'Needs Verification')
                    st.markdown(f"<span style='color:{color};font-weight:bold'>{label_text}</span> <span style='color:gray'>(Confidence: {conf:.1f}%)</span>", unsafe_allow_html=True)
                    st.write('---')
            else:
                st.error(f'API Error: {response.status_code} - {response.text}')
        except Exception as e:
            st.error(f'Error contacting analysis service: {e}') 