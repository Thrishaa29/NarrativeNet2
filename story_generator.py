import os
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# ✅ Load your Hugging Face key from .env
import streamlit as st
from huggingface_hub import InferenceClient

# Load Hugging Face API Key from Streamlit Secrets
hf_token = st.secrets["HF_API_KEY"]

# Show if token is loaded (for debug)
st.write("Token loaded:", bool(hf_token))

# Initialize Nebius client
client = InferenceClient(
    model="microsoft/phi-2",  # Replace with actual model name you're using
    provider="nebius",
    api_key=hf_token,
)

# Inference example
prompt = "Once upon a time in a magical forest,"
response = client.text_generation(prompt, max_new_tokens=50)
st.write("Generated Text:", response)



@st.cache_data
def generate_novel_cached(genre, user_prompt="", num_chapters=3):
    return generate_novel(genre, user_prompt, num_chapters)

def generate_novel(genre, user_prompt="", num_chapters=3):
    try:
        genre_descriptions = {
            "Fantasy": "A magical tale of wizards, kingdoms, and mythical creatures.",
            "Sci-Fi": "A futuristic story of technology, space, or artificial intelligence.",
            "Mystery": "A suspenseful investigation with clues and a twist.",
            "Adventure": "A journey through exotic lands filled with challenges and rewards.",
            "Horror": "A chilling narrative with fear, suspense, and supernatural events."
        }

        system_instruction = (
            f"You are a creative novelist. Write a well-structured {genre} novel in {num_chapters} chapters. "
            "Each chapter must start with '## Chapter X: Title'. "
            "Ensure the story has a beginning, middle, and ending. Use markdown format."
        )

        user_prompt_full = f"Genre: {genre}\nDescription: {genre_descriptions.get(genre, '')}\n"
        if user_prompt.strip():
            user_prompt_full += f"User Prompt: {user_prompt.strip()}"

        response = client.chat.completions.create(
            model="microsoft/phi-4",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt_full}
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating story with Phi-4 via Nebius: {e}"

def split_into_chapters(novel_text):
    chapters = []
    current_chapter = ""
    lines = novel_text.split('\n')

    for line in lines:
        if line.startswith('## Chapter '):
            if current_chapter:
                chapters.append(current_chapter.strip())
            current_chapter = line + "\n"
        else:
            current_chapter += line + "\n"

    if current_chapter:
        chapters.append(current_chapter.strip())

    return chapters
