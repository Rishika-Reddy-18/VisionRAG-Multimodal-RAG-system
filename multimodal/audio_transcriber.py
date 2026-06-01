

import whisper
import streamlit as st


@st.cache_resource
def load_model():

    return whisper.load_model("small")


def transcribe_audio(file_path):

    model = load_model()

    result = model.transcribe(
        file_path,
        fp16=False
    )

    return result["text"]

