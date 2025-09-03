import streamlit as st
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from heapq import nlargest
import os

nltk.download('punkt')
nltk.download('stopwords')

def extract_text(article_link):
    response = requests.get(article_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    return ' '.join(p.text for p in soup.find_all('p'))

def summarize_text(text, num_sentences=3):
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words("english"))
    word_freq = {}
    for word in nltk.word_tokenize(text):
        if word.lower() not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    sent_scores = {}
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_freq and len(sentence.split(' ')) < 30:
                sent_scores[sentence] = sent_scores.get(sentence, 0) + word_freq[word]

    summary_sentences = nlargest(num_sentences, sent_scores, key=sent_scores.get)
    return ' '.join(summary_sentences)

def text_to_audio(text, filename):
    tts = gTTS(text)
    tts.save(filename)

def main():
    st.title("Article to Audio Converter")

    article_link = st.text_input("Enter the link to the article:")

    if st.button("Convert to Audio"):
        if article_link:
            article_text = extract_text(article_link)
            full_audio_filename = "full_audio.mp3"
            text_to_audio(article_text, full_audio_filename)
            with open(full_audio_filename, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")

            summary = summarize_text(article_text)
            st.subheader("Summary:")
            st.text(summary)

            summary_audio_filename = "summary_audio.mp3"
            text_to_audio(summary, summary_audio_filename)
            with open(summary_audio_filename, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")

            os.remove(full_audio_filename)
            os.remove(summary_audio_filename)
        else:
            st.warning("Please enter a valid article link.")

if __name__ == "__main__":
    main()
