import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

# -------------------------------------------------
# Load API Key
# -------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("GOOGLE_API_KEY not found in .env file")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# Find first WORKING model dynamically
# -------------------------------------------------
@st.cache_resource
def find_working_model():
    models = client.models.list()

    test_prompt = "Say hello in one short sentence."

    for m in models:
        try:
            response = client.models.generate_content(
                model=m.name,
                contents=test_prompt
            )
            if response and response.text:
                return m.name
        except Exception:
            continue

    raise RuntimeError("No usable Gemini text model found for this API key")

MODEL_NAME = find_working_model()

# -------------------------------------------------
# Text generation helper
# -------------------------------------------------
def generate_text(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text

# -------------------------------------------------
# App logic
# -------------------------------------------------
def get_joke():
    return generate_text("Tell me a short, clean programmer joke.")

def generate_recipe(topic, word_count):
    prompt = f"""
    Write a detailed recipe blog.

    Topic: {topic}
    Length: approximately {word_count} words

    Include:
    - Introduction
    - Ingredients
    - Step-by-step cooking instructions
    - Tips and variations
    - Conclusion

    Write in a natural, blog-friendly style.
    """
    return generate_text(prompt)

# -------------------------------------------------
# Streamlit UI
# -------------------------------------------------
st.set_page_config(page_title="Flavour Fusion 🍽️", layout="centered")

st.title("🍽️ Flavour Fusion: AI-Driven Recipe Blogging")
st.caption(f"Using Gemini model: {MODEL_NAME}")

topic = st.text_input("Enter Recipe Topic")
word_count = st.slider("Select Word Count", 300, 2000, 800)

if st.button("Generate Recipe Blog"):
    if not topic.strip():
        st.warning("Please enter a recipe topic.")
    else:
        with st.spinner("Generating content... 🍳"):
            joke = get_joke()
            recipe_blog = generate_recipe(topic, word_count)

        st.subheader("😂 Programmer Joke")
        st.success(joke)

        st.subheader("📖 Generated Recipe Blog")
        st.write(recipe_blog)
