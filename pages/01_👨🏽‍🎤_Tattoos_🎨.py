import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import nltk
import altair as alt
from nltk.tokenize import RegexpTokenizer
from collections import Counter
from wordcloud import WordCloud
from PIL import Image


st.set_page_config(
    page_title="Florida Inmates and Their Tattoos",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This app will provide insite on Florida prisoners' tattoos and charges."
    }
)


@st.cache
def load_data():
    scars = pd.read_parquet('./data/tattoos.parquet')
    inmate_summary = pd.read_parquet('./data/inmate_summary.parquet')
    tattoo_location = list(scars.Location.unique())
    tattoo_location.append('ALL')
    tattoo_location.sort()
    return scars, inmate_summary, tattoo_location


def get_words(df, column='text_token', is_tattoo=False):
    if 'tatt_location' in st.session_state and is_tattoo:
        tatt_location = st.session_state['tatt_location']
        if tatt_location not in ['ALL', 'UNKNOWN']:
            df = df.loc[df['Location'] == tatt_location]
    return ' '.join(list(np.concatenate([c for c in df[column]]).flat))


@st.cache
def generate_wc(words, img='./data/flor_img_white.png', width=1800, height=800, stopwords=[], colormap='gnuplot'):
    mask = np.array(Image.open(img))
    wc = WordCloud(mode='RGBA', width=width, height=height,
                   background_color=None, max_words=3000, mask=mask, colormap=colormap, stopwords=stopwords)
    return wc.generate(words)


scars, inmate_summary, tattoo_location = load_data()
with st.sidebar:
    tatt_location = st.selectbox(
        'Tattoo Location', tattoo_location, key='tatt_location', index=0)
all_tattoos = get_words(scars, is_tattoo=True)
all_charges_text = get_words(inmate_summary, column='charge_tokens')
stop_words = ['hand', 'arm', 'forearm', 'chest', 'upper', 'right', 'left', 'and',
              'back', 'leg', 'hand', 'foot', 'right', 'cheek', 'finger', 'neck', 'behind', 'head', 'on', 'ear', 'r', 'l', 'forehead', 'side', 'of', 'face', 'lt', 'rt', 'eye']
wc_tatts = generate_wc(
    all_tattoos, stopwords=stop_words, colormap='gnuplot')
wc_charges = generate_wc(
    all_charges_text, height=1200, img='./data/florida_text_5.png')
st.header(f'Floridian Inmate Tattoos')
tab1, tab2 = st.tabs(['Overview', 'pyLDAvis'])
with tab1:
    ccol1, ccol2 = st.columns([4, 1])
    tcol1, tcol2 = st.columns([1, 4])
    with ccol1:
        st.image(wc_charges.to_image())
    with ccol2:
        st.markdown(
            '### The Florida letters wordcloud highlight the most common words in the charges associated to inmate crimes. ')

    with tcol1:
        st.markdown(
            '### The Florida state represents the most common tattoos associated to inmates.')
    with tcol2:
        st.image(wc_tatts.to_image())
with tab2:
    st.markdown(f'''
                ## Tattoo pyLDAvis
                The pyLDAvis visualization below helps interpret the 5 topics extracted from the Gensim LDA model.
                ''')
    with open('./data/tattoo_pyLDAvis.html', 'r') as html_file:
        html_string = html_file.read()
        components.html(html_string, width=1200,
                        height=1200, scrolling=True)
