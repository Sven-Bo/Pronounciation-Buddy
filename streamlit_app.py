import re
import streamlit as st
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pandas as pd
import time
from datetime import datetime

# Set Streamlit page configuration
st.set_page_config(
    page_title="IPA Pronunciation Extractor",
    page_icon="🔊",
    layout="centered",
    initial_sidebar_state="auto",
)

# Load secrets
API_KEY = st.secrets["api"]["API_KEY"]
SERVICE_URL = st.secrets["api"]["SERVICE_URL"]
VOICE = "en-GB_CharlotteV3Voice"
FORMAT = "IPA"

# Authenticate with IBM Watson
authenticator = IAMAuthenticator(API_KEY)
text_to_speech = TextToSpeechV1(authenticator=authenticator)
text_to_speech.set_service_url(SERVICE_URL)


# Function to get IPA pronunciation for each word
def get_ipa(word):
    try:
        pronunciation_result = text_to_speech.get_pronunciation(
            text=word, voice=VOICE, format=FORMAT
        ).get_result()
        ipa_pronunciation = pronunciation_result["pronunciation"]
        # Clean up the pronunciation string
        cleaned_pronunciation = re.sub(
            r"^[`'\[\].]+|[`'\[\].]+$", "", ipa_pronunciation
        )
        return cleaned_pronunciation
    except Exception as e:
        return None


# Streamlit app layout
st.title("🔊 IPA Pronunciation Extractor 🎉")
st.write(
    "Enter the text below and select the target sound you want to practice (e.g., æ, θ, etc.)."
)

# Default text for input
default_text = (
    "Hi, I'm Sven, the creator of the CutePlots Excel add-in. "
    "As a former data analyst, I know that presentations in a business setting aren't always super fun. "
    "That's why I made CutePlots – to add some fun to office meetings with cartoon-style charts. "
    "Let me show you how quick and easy it is to turn boring Excel data into eye-catching, cartoon charts "
    "and simple dashboards that'll make your colleagues smile."
)

# Text area for input text
input_text = st.text_area(
    "📝 Input Text",
    height=200,
    value=default_text,
    help="Enter the text you want to process.",
)

# Dropdown for target sound
sounds = ["æ", "θ", "ð", "ʃ", "ʒ", "ŋ", "ɑ", "ɪ", "ʊ", "ɔ", "ə"]
target_sound = st.selectbox(
    "🔤 Target Sound (IPA format)",
    sounds,
    help="Select the IPA symbol of the target sound.",
)

# Text area for words to ignore
words_to_ignore_input = st.text_input(
    "❌ Words to Ignore (comma-separated)",
    help="Optionally enter words to ignore, separated by commas.",
)

# Process button
if st.button("🚀 Process"):
    if not input_text:
        st.error("Please enter some text to process.")
    elif not target_sound:
        st.error("Please select a target sound.")
    else:
        text = input_text.lower()  # Convert text to lower case

        # Extract words from the text and remove duplicates
        words = list(set(re.findall(r"\b\w+\b", text)))
        words.sort()  # Sort words alphabetically

        # Filter out the words to ignore
        words_to_ignore = set(words_to_ignore_input.lower().split(","))
        words = [word for word in words if word not in words_to_ignore]

        # Initialize an empty DataFrame for storing the results
        columns = ["Word", "IPA"]
        df = pd.DataFrame(columns=columns)

        # Initialize progress bar
        progress_text = "🔄 Processing... Hang tight, this won't take long! ⏳"
        my_bar = st.progress(0, text=progress_text)

        total_words = len(words)

        # Process each word
        for idx, word in enumerate(words):
            ipa_pronunciation = get_ipa(word)

            if ipa_pronunciation and target_sound in ipa_pronunciation:
                new_row = pd.DataFrame({"Word": [word], "IPA": [ipa_pronunciation]})
                df = pd.concat([df, new_row], ignore_index=True)

            # Update progress bar
            my_bar.progress((idx + 1) / total_words, text=progress_text)

        my_bar.empty()

        if not df.empty:
            # Display the results
            st.balloons()
            st.write("🎉 IPA pronunciations with the target sound:")
            st.dataframe(df)

            st.write("📥 You can also download the data as an Excel file if needed.")
            # Option to download the results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"ipa_pronunciations_{target_sound}_{timestamp}.xlsx"
            df.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download Excel",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        else:
            st.info(
                "No words found with the target sound in the text. Please try again with a different text or target sound."
            )
