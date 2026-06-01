import streamlit as st
import os
import uuid

from streamlit_mic_recorder import mic_recorder

from auth.register import register_user
from auth.login import login_user
from auth.admin import admin_panel

from utils.file_handler import save_uploaded_file

from multimodal.image_ocr import extract_text_from_image
from multimodal.audio_transcriber import transcribe_audio
from multimodal.video_processor import extract_audio
from multimodal.text_cleaner import clean_text
from multimodal.pdf_reader import extract_text_from_pdf

from rag.pipeline import process_text
from rag.vector_store import clear_vector_db
from rag.retriever import retrieve
from rag.llm import generate_answer


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="VisionRAG",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 VisionRAG")
st.caption("Multimodal Conversational RAG System")


# =========================
# UI STYLE
# =========================

st.markdown("""
<style>
html, body {
    font-size: 18px !important;
}

.stChatMessage, .stChatMessage * {
    font-size: 18px !important;
    line-height: 1.6 !important;
}

.stApp {
    background: #0e1117 !important;
}

.block-container {
    max-width: 100% !important;
    padding-bottom: 8rem;
}
</style>
""", unsafe_allow_html=True)


# =========================
# SESSION STATE
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "document_ready" not in st.session_state:
    st.session_state.document_ready = False

if "processed_file" not in st.session_state:
    st.session_state.processed_file = ""

if "show_upload_menu" not in st.session_state:
    st.session_state.show_upload_menu = False

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True


# =========================================================
# 🔐 AUTH GATE
# =========================================================

if not st.session_state.logged_in:

    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":
        login_user()

    elif menu == "Register":
        register_user()

    st.stop()


# =========================================================
# 🏠 SIDEBAR
# =========================================================

st.sidebar.title("🤖 VisionRAG")

if st.sidebar.button("📌 Toggle Sidebar"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open
    st.rerun()

if st.sidebar.button("➕ New Chat"):
    chat_name = f"Chat {len(st.session_state.chat_sessions)+1}"
    st.session_state.chat_sessions[chat_name] = []
    st.session_state.current_chat = chat_name
    st.rerun()

st.sidebar.subheader("💬 Chat History")

for chat_name in st.session_state.chat_sessions.keys():
    if st.sidebar.button(chat_name, key=f"chat_{chat_name}"):
        st.session_state.current_chat = chat_name
        st.rerun()

st.sidebar.divider()

st.sidebar.write(f"👤 Logged in as: {st.session_state.user}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.chat_sessions = {"Chat 1": []}
    st.session_state.current_chat = "Chat 1"
    st.session_state.document_ready = False
    st.session_state.processed_file = ""
    st.session_state.show_upload_menu = False
    st.rerun()


# =========================
# CHAT INPUT RESPONSIVE WIDTH
# =========================

input_left = "25%" if st.session_state.sidebar_open else "10%"
input_right = "5%" if st.session_state.sidebar_open else "10%"

st.markdown(f"""
<style>
[data-testid="stChatInput"] {{
    position: fixed;
    bottom: 20px;
    left: {input_left};
    right: {input_right};
    transition: all 0.3s ease-in-out;
}}
</style>
""", unsafe_allow_html=True)


# =========================
# HOME UI
# =========================

st.success(f"Welcome {st.session_state.user}")
st.divider()


# =========================
# CHAT HISTORY DISPLAY
# =========================

current_messages = st.session_state.chat_sessions[
    st.session_state.current_chat
]

for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================
# INPUT AREA
# =========================

col1, col2, col3 = st.columns([1, 1, 8])

with col1:
    if st.button("➕"):
        st.session_state.show_upload_menu = True

with col2:
    mic_audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹",
        format="wav"
    )

with col3:
    query = st.chat_input("Ask anything about your documents...")


# =========================
# UPLOAD MENU
# =========================

uploaded_file = None

if st.session_state.show_upload_menu:
    upload_type = st.radio(
        "Upload Type",
        ["🖼️ Image", "📄 PDF", "🎵 Audio", "🎥 Video"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if upload_type == "🖼️ Image":
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    elif upload_type == "📄 PDF":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    elif upload_type == "🎵 Audio":
        uploaded_file = st.file_uploader("Upload Audio", type=["mp3", "wav"])

    elif upload_type == "🎥 Video":
        uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])


# =========================
# ✅ ADDED: FILE PREVIEW (NEW FEATURE)
# =========================

if uploaded_file:
    st.info(f"📁 Uploaded: {uploaded_file.name}")

    file_ext = uploaded_file.name.lower().split(".")[-1]

    if file_ext in ["png", "jpg", "jpeg"]:
        st.image(uploaded_file, caption="🖼️ Image Preview")

    elif file_ext in ["mp3", "wav"]:
        st.audio(uploaded_file)

    elif file_ext in ["mp4", "avi", "mov"]:
        st.video(uploaded_file)

    elif file_ext == "pdf":
        st.success("📄 PDF uploaded successfully (preview not supported)")


# =========================
# FILE PROCESSING
# =========================

if uploaded_file:
    filename = uploaded_file.name

    if st.session_state.processed_file != filename:
        path = save_uploaded_file(uploaded_file, "uploads")

        try:
            extracted_text = ""

            if filename.lower().endswith(("png", "jpg", "jpeg")):
                extracted_text = clean_text(extract_text_from_image(path))

            elif filename.lower().endswith(".pdf"):
                extracted_text = clean_text(extract_text_from_pdf(path))

            elif filename.lower().endswith(("mp3", "wav")):
                extracted_text = clean_text(transcribe_audio(path))

            elif filename.lower().endswith(("mp4", "avi", "mov")):
                audio_path = extract_audio(path)
                if audio_path:
                    extracted_text = clean_text(transcribe_audio(audio_path))

            if extracted_text.strip():
                clear_vector_db()
                process_text(extracted_text)

                st.session_state.document_ready = True
                st.session_state.processed_file = filename
                st.session_state.show_upload_menu = False

                st.success("📎 File added to knowledge base")
                st.rerun()

        except Exception as e:
            st.error(f"Processing failed: {e}")


# =========================
# MIC PROCESSING
# =========================

if mic_audio:
    os.makedirs("uploads", exist_ok=True)
    audio_path = f"uploads/mic_{uuid.uuid4().hex}.wav"

    try:
        with open(audio_path, "wb") as f:
            f.write(mic_audio["bytes"])

        extracted_text = clean_text(transcribe_audio(audio_path))

        if extracted_text.strip():
            clear_vector_db()
            process_text(extracted_text)

            st.session_state.document_ready = True
            st.session_state.processed_file = "Voice Recording"
            st.session_state.show_upload_menu = False

            st.success("🎤 Voice added to knowledge base")
            st.rerun()

    except Exception as e:
        st.error(f"Mic processing failed: {e}")


# =========================
# CHAT PROCESSING
# =========================

if query:
    st.session_state.chat_sessions[
        st.session_state.current_chat
    ].append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    if not st.session_state.document_ready:
        answer = "Please upload a document, image, audio or video first."
    else:
        clean_query = clean_text(query)
        docs = retrieve(clean_query)
        context = "\n\n".join([d.page_content for d in docs]) if docs else ""
        answer = generate_answer(clean_query, context)

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.chat_sessions[
        st.session_state.current_chat
    ].append({"role": "assistant", "content": answer})