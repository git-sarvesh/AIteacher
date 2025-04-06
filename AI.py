import json
import streamlit as st
import pyttsx3
from gtts import gTTS
import os
import google.generativeai as genai
from dotenv import load_dotenv
import pygame
import logging

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
        if avg_marks is None or avg_marks < 50:
            prompt = f"Explain this in a simple and short way: {question}"
        else:
            prompt = f"Explain this in detail: {question}"
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

# ----------- Streamlit UI ---------------------------
st.set_page_config(page_title="AI Teacher Bot", page_icon="🤖")
st.title("🤖 AI Teacher Bot")
st.subheader("Ask doubts and learn with your AI teacher!")

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

    question = st.text_area("Enter your doubt:")
    if st.button("Get Answer") and question:
        answer = get_gemini_answer(question, avg_marks)
        st.info(answer)
        speak(answer)
