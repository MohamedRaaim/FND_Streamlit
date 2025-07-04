import streamlit as st
import requests
import re

st.title('Fake News Detector')
st.write('Enter a news snippet below.')

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

def get_confidence_color(score, label):
    if score >= 85:
        return 'green' if label == 'REAL' else 'red'
    if score > 50:
        return 'yellow'
    return 'gray'

def get_display_label(label, conf=None):
    if conf is not None and 50 < conf < 85:
        return 'Needs Verification'
    if label == 'REAL':
        return 'Likely True'
    if label == 'FAKE':
        return 'Likely Fake'
    return 'Needs Verification'

def map_conf_to_bar(conf, label):
    if label == 'FAKE':
        return conf / 2  # 0-100% confidence -> 0-50% of bar
    elif label == 'REAL':
        return (conf / 2) + 50  # 0-100% confidence -> 50-100% of bar
    else:
        return 50  # Center for 'Needs Verification' or unknown

def confidence_bar(conf, label):
    color = get_confidence_color(conf, label)
    bar_pos = map_conf_to_bar(conf, label)
    bar_html = f"""
    <div style='width: 80%; margin: 16px 0;'>
      <div style='position: relative; height: 32px; width: 100%;'>
        <div style='position: absolute; left: 0; top: 12px; height: 8px; width: 100%; border-radius: 4px; background: linear-gradient(to right, red 0%, red 50%, yellow 50%, yellow 85%, green 85%, green 100%);'></div>
        <div style='position: absolute; left: {bar_pos}%; top: 8px; transform: translateX(-50%); z-index: 2;'>
          <span style='font-size: 22px; color: #fff; text-shadow: 0 0 2px #222;'>▲</span>
        </div>
      </div>
      <div style='text-align: center; margin-top: 2px; font-size: 13px; font-weight: bold;'>
        Confidence: {conf:.1f}% | Label: {get_display_label(label, conf)}
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
                    color = get_confidence_color(conf, label)
                    label_text = get_display_label(label, conf)
                    st.markdown(f"<span style='color:{color};font-weight:bold'>{label_text}</span> <span style='color:gray'>(Confidence: {conf:.1f}%)</span>", unsafe_allow_html=True)
                    confidence_bar(conf, label)
                    st.write('---')
            else:
                st.error(f'API Error: {response.status_code} - {response.text}')
        except Exception as e:
            st.error(f'Error contacting analysis service: {e}') 