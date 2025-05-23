
import streamlit as st

# ✅ FIRST Streamlit command
st.set_page_config(page_title="Novel Generator", layout="wide")
from story_generator import generate_novel_cached, split_into_chapters
from tts import speak
import os
from dotenv import load_dotenv
load_dotenv()


# Check if CSS file exists before trying to read it
if os.path.exists("themes.css"):
    st.markdown(
        "<style>" + open("themes.css").read() + "</style>",
        unsafe_allow_html=True
    )
else:
    # Define basic styling if CSS file is missing
    st.markdown("""
    <style>
    body {
        background-color: #1e1e2f;
        color: #ffffff;
    }
    h1, h2, h3 {
        color: #ffcc70;
    }
    .stButton>button {
        background-color: #ff7e5f;
        color: white;
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 NarrativeNet: AI-Driven Novel Generation and Narration")

# Add an intro message
st.markdown("""
Welcome to the Novel Generator! Create complete novels in your favorite genre.
Choose a genre below and optionally add your own beginning to the story.
""")

# Add session state to track novel generation
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'novel' not in st.session_state:
    st.session_state.novel = None
if 'current_chapter' not in st.session_state:
    st.session_state.current_chapter = 0

# Genre selection with descriptions
genre_options = {
    "Fantasy": "Fantasy (magic, creatures, quests)",
    "Sci-Fi": "Sci-Fi (technology, space, aliens)",
    "Mystery": "Mystery (detectives, cases, clues)",
    "Adventure": "Adventure (exploration, treasure, journeys)",
    "Horror": "Horror (suspense, fear, supernatural)"
}
genre = st.selectbox(
    "Select Novel Genre", 
    list(genre_options.keys()),
    format_func=lambda x: genre_options[x]
)

# User prompt with clear instruction
user_prompt = st.text_input(
    "Your Novel Beginning (optional)", 
    placeholder="Enter a few words to start your novel or leave empty for a genre-appropriate beginning"
)

# Chapter length selector - REDUCED max for faster generation
chapter_count = st.slider("Number of Chapters", min_value=2, max_value=5, value=3)

# Text-to-speech option
enable_tts = st.checkbox("Enable Text-to-Speech for Chapter Reading", value=False)

import os  # Make sure this is at the top of your file

def display_novel(novel_text, current_idx, enable_tts):
    if novel_text.startswith("Error"):
        st.error(novel_text)
        return

    # Extract title
    title_line = novel_text.split('\n')[0] if '\n' in novel_text else "Generated Novel"
    title = title_line.replace('# ', '') if title_line.startswith('# ') else title_line
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)

    # Split into chapters
    chapters = split_into_chapters(novel_text)

    # Table of contents
    with st.expander("📑 Table of Contents", expanded=True):
        for i, chapter in enumerate(chapters):
            chapter_title = chapter.split('\n')[0] if '\n' in chapter else f"Chapter {i+1}"
            if st.button(chapter_title, key=f"toc_{i}"):
                st.session_state.current_chapter = i
                st.rerun()

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if current_idx > 0 and st.button("◀️ Previous"):
            st.session_state.current_chapter -= 1
            st.rerun()
    with col3:
        if current_idx < len(chapters) - 1 and st.button("Next ▶️"):
            st.session_state.current_chapter += 1
            st.rerun()

    # Full-width separator and content
    st.markdown("---")
    current_chapter = chapters[current_idx]
    st.markdown(current_chapter, unsafe_allow_html=True)

    # ✅ Text-to-Speech
    if enable_tts:
        chapter_lines = current_chapter.split('\n')
        chapter_text = '\n'.join([line for line in chapter_lines if not line.startswith('#')])
        if st.button("🔊 Read Chapter Aloud", key=f"read_{current_idx}"):
            try:
                from tts import speak  # Import inside to avoid circular issues
                audio_path = speak(chapter_text)
                if audio_path and os.path.exists(audio_path):
                    st.audio(audio_path, format="audio/wav")
                else:
                    st.warning("Could not generate audio.")
            except Exception as e:
                st.warning(f"Text-to-speech unavailable: {e}")


def generate_button_callback():
    st.session_state.generating = True
    st.session_state.novel = None
    st.session_state.current_chapter = 0

# Create a button with custom styling
generate_btn = st.button(
    "✨ Generate Novel", 
    on_click=generate_button_callback,
    key="generate_novel"
)

# Show generation process - SIMPLIFIED
if st.session_state.generating:
    progress_placeholder = st.empty()
    with progress_placeholder.container():
        st.write("🔮 Generating your novel... Please wait. This might take 30-60 seconds.")
        st.progress(50)  # Show an indeterminate progress bar
    
    try:
        # Use the cached version of generate_novel for speed
        novel = generate_novel_cached(genre, user_prompt, num_chapters=chapter_count)
        st.session_state.novel = novel
        st.session_state.generating = False
        
        # Clear progress indicators
        progress_placeholder.empty()
        
        # Force a rerun to display the novel
        st.experimental_rerun()
            
    except Exception as e:
       
        st.session_state.generating = False

# Display novel if available
if not st.session_state.generating and st.session_state.novel:
    display_novel(st.session_state.novel, st.session_state.current_chapter, enable_tts)


    
    # Download button for the novel
    st.download_button(
        label="📥 Download Novel as Text",
        data=st.session_state.novel,
        file_name=f"{genre.lower()}_novel.txt",
        mime="text/plain"
    )