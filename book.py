import streamlit as st
import requests
from bs4 import BeautifulSoup
import pyttsx3
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from heapq import nlargest
import os

# Download NLTK resources if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Function to extract text from the article link
def extract_text(article_link):
    try:
        response = requests.get(article_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from HTML
        article_text = ' '.join([p.text for p in soup.find_all('p')])
        return article_text
    except:
        return None

# Function to summarize the article text
def summarize_text(text, num_sentences=3):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    
    # Calculate word frequencies
    word_freq = {}
    for word in nltk.word_tokenize(text):
        if word.lower() not in stop_words:
            if word not in word_freq.keys():
                word_freq[word] = 1
            else:
                word_freq[word] += 1
                
    # Calculate sentence scores based on word frequencies
    sent_scores = {}
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_freq.keys():
                if len(sentence.split(' ')) < 30:
                    if sentence not in sent_scores.keys():
                        sent_scores[sentence] = word_freq[word]
                    else:
                        sent_scores[sentence] += word_freq[word]
    
    # Select top sentences based on scores
    summary_sentences = nlargest(num_sentences, sent_scores, key=sent_scores.get)
    
    # Join summary sentences to form summary
    summary = ' '.join(summary_sentences)
    
    return summary

# Function to convert text to audio
def text_to_audio(text, filename):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.save_to_file(text, filename)
    engine.runAndWait()

# Streamlit application
def main():
    st.title("Article to Audio Converter")
    
    # Accept article link from user
    article_link = st.text_input("Enter the link to the article:")
    
    if st.button("Convert to Audio"):
        if article_link:
            article_text = extract_text(article_link)
            if article_text:
                # Convert full text to audio
                full_audio_filename = "full_audio.mp3"
                text_to_audio(article_text, full_audio_filename)
                
                # Display the full audio clip
                with open(full_audio_filename, "rb") as audio_file:
                    full_audio_bytes = audio_file.read()
                    st.audio(full_audio_bytes, format="audio/mp3")
                
                # Summary Text
                summary = summarize_text(article_text)
                st.subheader("Summary:")
                st.text(summary)
                
                # Convert summary text to audio
                summary_audio_filename = "summary_audio.mp3"
                text_to_audio(summary, summary_audio_filename)
                
                # Display the summary audio clip
                with open(summary_audio_filename, "rb") as audio_file:
                    summary_audio_bytes = audio_file.read()
                    st.audio(summary_audio_bytes, format="audio/mp3")
                
                # Delete the temporary audio files
                os.remove(full_audio_filename)
                os.remove(summary_audio_filename)
            else:
                st.error("Failed to fetch or convert the article. Please check the link.")
        else:
            st.warning("Please enter a valid article link.")

if __name__ == "__main__":
    main()
