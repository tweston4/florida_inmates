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
from bokeh.plotting import figure, output_file, show
from bokeh.models import Label
from bokeh.io import output_notebook
import matplotlib.colors as mcolors


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


def generate_wc(words, img='./data/flor_img_white.png', width=900, height=600, stopwords=[], colormap='gnuplot'):
    mask = np.array(Image.open(img))
    wc = WordCloud(mode='RGBA', width=width, height=height,
                   background_color=None, max_words=3000, mask=mask, colormap=colormap, stopwords=stopwords)
    return wc.generate(words)


def plot_tsne(num_topics=4, colors=mcolors.TABLEAU_COLORS.items()):
    arr = pd.read_parquet('./data/topic_weights.parquet').values
    # Keep the well separated points (optional)
    arr = arr[np.amax(arr, axis=1) > 0.35]
    # Dominant topic number in each doc
    topic_num = np.argmax(arr, axis=1)

    tsne_lda = pd.read_csv('./data/tsne_lda.csv')
    mycolors = np.array([color for name, color in colors])
    plot = figure(title="t-SNE Clustering of {} LDA Topics".format(num_topics),
                  width=900, height=700)
    plot.scatter(x=tsne_lda.iloc[:, 1].values,
                 y=tsne_lda.iloc[:, 2].values, color=mycolors[topic_num])
    return plot


def topic_summary():
    df = pd.read_parquet('./data/topic_summary.parquet')

    topic_by_count = alt.Chart(df).mark_bar().encode(
        y=alt.Y('topic_id:N', axis=None, title='Topics'),
        x=alt.X('count:Q', title='Number of Tattoos by Dominant Topic',
                sort=alt.SortOrder('descending')),
        color=alt.Color('topic_id:N', legend=None,
                        scale=alt.Scale(scheme='category20c')),
        tooltip=[
            alt.Tooltip('topic_text:N', title='Name'),
            alt.Tooltip('top_3:N', title='Top 3'),
            alt.Tooltip('count:Q', title='Total')
        ]
    ).properties(
        width=400,
        height=300
    )

    topic_label = alt.Chart(df).mark_text().encode(
        y=alt.Y('topic_text:N', axis=None),
        text=alt.Text('topic_text:N')

    ).properties(width=40,
                 height=300)

    topic_by_weight = alt.Chart(df).mark_bar().encode(
        y=alt.Y('topic_id:N', axis=None, title='Topics'),
        x=alt.X('countweighted:Q', title='Number of Tattoos by Topic Weightage'),
        color=alt.Color('topic_id:N', legend=None,
                        scale=alt.Scale(scheme='category20c')),
        tooltip=[
            alt.Tooltip('topic_text:N', title='Name'),
            alt.Tooltip('top_3:N', title='Top 3'),
            alt.Tooltip('countweighted:Q', title='Sum of Weights')
        ]
    ).properties(
        width=400,
        height=300
    )

    return alt.concat(topic_by_count, topic_label, topic_by_weight, spacing=0)


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
st.image(wc_charges.to_image())
st.markdown(
    'Analyze the tattoo description for individuals in the Florida prison systme. Each tab will provide insight of the topic modeling methods used to analyze the text data.')
tab1, tab2, tab3, tab4 = st.tabs(['Overview', 'LDA', 't-SNE', 'pyLDAvis'])
with tab1:
    st.markdown('''
                ### Tattoo WordCloud
                                
                Update the Tattoo Location in the side bar to see the most popular tattoos for that body part.
                ''')
    st.image(wc_tatts.to_image())

with tab2:
    st.markdown('''
                ### LDA
                
                 LDA is most commonly used to discover a user-specified number of topics shared by documents within a text corpus. Here each observation is a document, the features are the presence (or occurrence count) of each word, and the categories are the topics. Since the method is unsupervised, the topics are not specified up front, and are not guaranteed to align with how a human may naturally categorize documents. The topics are learned as a probability distribution over the words that occur in each document. Each document, in turn, is described as a mixture of topics.
                ''')
    img_col1, img_col2 = st.columns(2)
    with img_col1:
        sent_topic = Image.open('./data/sent_topic_coloring.png')
        st.image(sent_topic)
    with img_col2:
        tp_summ = topic_summary()
        st.altair_chart(tp_summ)


with tab3:
    st.markdown('''
                ### t-SNE
                
                t-SNE is a tool to visualize high-dimensional data. It converts similarities between data points to joint probabilities and tries to minimize the Kullback-Leibler divergence between the joint probabilities of the low-dimensional embedding and the high-dimensional data. t-SNE has a cost function that is not convex, i.e. with different initializations we can get different results.
                ''')
    tsne = plot_tsne()
    st.bokeh_chart(tsne)


with tab4:
    st.markdown(f'''
                ## Tattoo pyLDAvis
                The pyLDAvis visualization below helps interpret the 5 topics extracted from the Gensim LDA model.
                ''')
    with open('./data/tattoo_pyLDAvis.html', 'r') as html_file:
        html_string = html_file.read()
        components.html(html_string, width=1200,
                        height=1200, scrolling=True)
