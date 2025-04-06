import json
import streamlit as st
import pyttsx3
from gtts import gTTS
import os
import google.generativeai as genai
from dotenv import load_dotenv
import pygame
import logging
from PIL import Image
import pytesseract

# Configure Tesseract path if needed (change this path to where Tesseract is installed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load .env and API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("API Key not found. Set GEMINI_API_KEY in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Setup Logging
logging.basicConfig(level=logging.INFO)

# ----------- Student Data Handling -----------------
def load_student_data(filename="students.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading student data: {e}")
        return []

def calculate_average(student_name, student_data):
    student = next((s for s in student_data if s["name"].lower() == student_name.lower()), None)
    if student:
        marks = list(student.get("subjects", {}).values())
        return sum(marks) / len(marks) if marks else None
    return None

# ----------- AI Answer Generator --------------------
def get_gemini_answer(question, avg_marks):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-001")
        if avg_marks is None:
            prompt = f"Answer briefly: {question}"
        elif avg_marks < 50:
            prompt = f"This student is weak. Explain simply and slowly: {question}"
        else:
            prompt = f"This student is strong. Provide a deep and detailed explanation: {question}"

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error fetching answer: {e}")
        return f"Error fetching answer: {e}"

# ----------- Text to Speech -------------------------
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        try:
            tts = gTTS(text)
            tts.save("temp.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("temp.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
            os.remove("temp.mp3")
        except Exception as e:
            logging.error(f"TTS failed: {e}")

# ----------- Extract Text from Image ----------------
def extract_text_from_image(image_file):
    try:
        img = Image.open(image_file)
        return pytesseract.image_to_string(img)
    except Exception as e:
        logging.error(f"Image processing failed: {e}")
        return ""

# ----------- Streamlit UI ---------------------------
st.set_page_config(page_title="AI Teacher Bot", page_icon="🤖")
st.title("🤖 AI Teacher Bot")
st.subheader("Ask your doubt by typing or uploading an image!")

student_data = load_student_data()
student_name = st.text_input("Enter your name:")

if student_name:
    avg_marks = calculate_average(student_name, student_data)
    if avg_marks is not None:
        feedback = f"Hi {student_name}, your average score is {avg_marks:.2f}."
    else:
        feedback = f"Hi {student_name}, we couldn't find your data."
    st.success(feedback)
    speak(feedback)

    st.markdown("### 📷 Upload an image of your doubt (optional)")
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    question = st.text_area("Or type your doubt here:")
    
    if st.button("Get Answer"):
        # Get question from image if uploaded
        if uploaded_file:
            question_from_img = extract_text_from_image(uploaded_file)
            st.markdown("**Extracted Text from Image:**")
            st.code(question_from_img)
            question = question_from_img if not question.strip() else question

        if question:
            answer = get_gemini_answer(question, avg_marks)
            st.info(answer)
            speak(answer)
        else:
            st.warning("Please type a doubt or upload an image.")
