import json
import streamlit as st
import pyttsx3
from gtts import gTTS
import os
import google.generativeai as genai
from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
import pygame  # Replacing playsound
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("API Key not found. Set GEMINI_API_KEY as an environment variable.")

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("API Key loaded successfully!")

genai.configure(api_key=GEMINI_API_KEY)

# Load Panda3D in headless mode
loadPrcFileData("", "window-type none")  
loadPrcFileData("", "audio-library-name null")  

def is_headless():
    """Detect if running in a headless environment."""
    return os.environ.get("DISPLAY") is None

# ----------- Singleton Wrapper for AIRobot -------------
class AIRobot(ShowBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIRobot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            try:
                super().__init__()
                self.initialized = True
                logging.info("✅ Panda3D running in headless mode")
            except Exception as e:
                st.warning(f"⚠️ Panda3D initialization failed: {e}")

# ----------- Student Data Handling -----------------
def load_student_data(filename="students.json"):
    """Loads student data from a JSON file."""
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading student data: {e}")
        return []

def save_student_data(data, filename="students.json"):
    """Saves student data back to the JSON file."""
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        logging.info("Student data saved successfully!")
    except Exception as e:
        logging.error(f"Error saving student data: {e}")

def calculate_average(student_name, student_data):
    """Calculates the average marks for a student."""
    student = next((s for s in student_data if s["name"].lower() == student_name.lower()), None)
    if student:
        marks = list(student.get("subjects", {}).values())
        return sum(marks) / len(marks) if marks else None
    return None

# ----------- AI Response + Voice -------------------
def get_gemini_answer(question, avg_marks):
    """Fetches an answer from Gemini AI, adjusting detail based on student performance."""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-001")
        if avg_marks is None:
            prompt = f"Provide a general explanation for: {question}"
        elif avg_marks < 50:
            prompt = f"Explain this in a short and simple way: {question}"
        else:
            prompt = f"Provide a detailed answer for: {question}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error fetching answer: {e}")
        return f"Error fetching answer: {e}"

def speak(text):
    """Converts text to speech with pyttsx3 or gTTS as a fallback."""
    if is_headless():
        logging.warning("⚠️ Skipping voice output in headless mode.")
        return
    try:
        engine = pyttsx3.init(driverName='sapi5')  # Use Windows speech engine
        voices = engine.getProperty('voices')  # Get available voices
        engine.setProperty('voice', voices[0].id)  # Use first voice
        engine.setProperty('rate', 150)  # Adjust speech speed
        engine.say(text)
        engine.runAndWait()
    except Exception:
        st.warning("⚠️ pyttsx3 failed, switching to gTTS...")
        try:
            tts = gTTS(text)
            tts.save("temp.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("temp.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
            os.remove("temp.mp3")  # Cleanup
        except Exception as e:
            logging.error(f"❌ Both pyttsx3 and gTTS failed: {e}")

# ----------- Streamlit UI --------------------------
st.title("🤖 AI Teacher Bot")
st.subheader("An AI-powered assistant for students!")

student_data = load_student_data()
student_name = st.text_input("Enter your name:", key="student_name_input")  # ✅ Unique key added

if student_name:
    avg_marks = calculate_average(student_name, student_data)
    feedback = (f"Hello {student_name}, your average score is {avg_marks:.2f}. Keep learning and improving!"
                if avg_marks is not None else 
                f"Hello {student_name}, I couldn't find your records. Keep working hard!")
    
    st.success(feedback)
    speak(feedback)  # ✅ Speak out the feedback

    if st.checkbox("Do you have any doubts?", key="doubt_checkbox"):  # ✅ Unique key added
        question = st.text_area("What is your doubt?", key="doubt_text_area")  # ✅ Unique key added
        if st.button("Ask AI", key="ask_ai_button") and question.strip():  # ✅ Unique key added
            answer = get_gemini_answer(question, avg_marks)
            st.info(answer)
            speak(answer)  # ✅ Speak out the AI answer

# ----------- Initialize AIRobot Singleton -----------
if "air_robot" not in st.session_state:
    try:
        st.session_state.air_robot = AIRobot()
    except Exception as e:
        logging.error(f"❌ Failed to initialize AI Robot: {e}")
