import streamlit as st
import requests
import re

st.title('Fake News Detector')
st.write('Enter a news snippet below. Every 3 sentences will be grouped and analyzed together.')

# Sidebar legend
st.sidebar.markdown('''
### Legend
<div style='display: flex; align-items: center; margin-bottom: 8px;'><span style='display:inline-block;width:20px;height:20px;background:green;border-radius:3px;margin-right:8px;'></span>Green: Likely true</div>
<div style='display: flex; align-items: center; margin-bottom: 8px;'><span style='display:inline-block;width:20px;height:20px;background:yellow;border-radius:3px;margin-right:8px;'></span>Yellow: Needs verification</div>
<div style='display: flex; align-items: center; margin-bottom: 8px;'><span style='display:inline-block;width:20px;height:20px;background:red;border-radius:3px;margin-right:8px;'></span>Red: Likely fake</div>
''', unsafe_allow_html=True)

user_input = st.text_area('News Snippet', height=200)

def group_sentences(sentences, n=3):
    return [' '.join(sentences[i:i+n]) for i in range(0, len(sentences), n)]

def confidence_bar(conf, label):
    # conf: 0-100
    # label: 'REAL', 'FAKE', or other
    # Bar: red (0-50), yellow (50-85), green (85-100)
    # Marker at conf
    bar_html = f"""
    <div style='width: 80%; margin: 16px 0;'>
      <div style='position: relative; height: 32px; width: 100%;'>
        <div style='position: absolute; left: 0; top: 12px; height: 8px; width: 100%; border-radius: 4px; background: linear-gradient(to right, red 0%, red 50%, yellow 50%, yellow 85%, green 85%, green 100%);'></div>
        <div style='position: absolute; left: 0; top: 0; width: 100%; display: flex; justify-content: space-between; font-size: 12px; color: #222;'>
          <span>0</span><span>100</span><span>0</span><span>100</span>
        </div>
        <div style='position: absolute; left: {conf}%; top: 6px; transform: translateX(-50%);'>
          <span style='font-size: 22px; color: #222;'>▼</span>
        </div>
      </div>
      <div style='text-align: center; margin-top: 2px; font-size: 13px; font-weight: bold;'>
        Confidence: {conf:.1f}% | Label: {label}
      </div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

if st.button('Analyze'):
    if not user_input.strip():
        st.warning('Please enter some text to analyze.')
    else:
        # Split input into sentences
        sentences = re.split(r'(?<=[.!?])\s+', user_input.strip())
        sentences = [s for s in sentences if s.strip()]
        groups = group_sentences(sentences, 3)
        payload = {"paragraphs": [{"text": g} for g in groups]}
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
                    st.markdown(f"{groups[idx]}")
                    label = result.get('label', 'UNKNOWN')
                    conf = result.get('confidence_score', 0)
                    color = 'green' if label == 'REAL' else ('red' if label == 'FAKE' else 'orange')
                    label_text = 'Likely True' if label == 'REAL' else ('Likely Fake' if label == 'FAKE' else 'Needs Verification')
                    st.markdown(f"<span style='color:{color};font-weight:bold'>{label_text}</span> <span style='color:gray'>(Confidence: {conf:.1f}%)</span>", unsafe_allow_html=True)
                    confidence_bar(conf, label_text)
                    st.write('---')
            else:
                st.error(f'API Error: {response.status_code} - {response.text}')
        except Exception as e:
            st.error(f'Error contacting analysis service: {e}') 