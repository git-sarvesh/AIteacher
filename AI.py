import json
import streamlit as st
import pyttsx3
from gtts import gTTS
import os
import google.generativeai as genai
from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase

# Configure Panda3D to run in headless mode
loadPrcFileData("", "window-type none")  # Prevents window creation
loadPrcFileData("", "audio-library-name null")  # Optional: Disables sound

# Configure Gemini AI
GEMINI_API_KEY = "AIzaSyCJ6a-YymLZ0RQUpO87JVTbtWcBnBixO88"
genai.configure(api_key=GEMINI_API_KEY)

# ----------- Panda3D Singleton Wrapper -------------
class AIRobot(ShowBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIRobot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Prevent multiple initializations
            ShowBase.__init__(self)
            self.initialized = True
            print("✅ Panda3D running in headless mode")

# ----------- Student Data Handling -----------------
def load_student_data(filename="students.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                st.error("Invalid JSON format. Expected a list of students.")
                return []
    except FileNotFoundError:
        st.error("Student data file not found.")
    except json.JSONDecodeError:
        st.error("Error decoding student data. Ensure the JSON file is correctly formatted.")
    return []

def calculate_average(student_name, student_data):
    student = next((s for s in student_data if s["name"].lower() == student_name.lower()), None)
    if student:
        marks = list(student.get("subjects", {}).values())
        if marks:
            return sum(marks) / len(marks)
    return None

# ----------- AI Response + Voice -------------------
def get_gemini_answer(question):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-001")
        response = model.generate_content(question)
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        return f"Error fetching answer: {e}"

def speak(text):
    try:
        engine = pyttsx3.init(driverName='sapi5')  # Force use of Windows speech engine
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"❌ Text-to-speech failed: {e}")
        try:
            tts = gTTS(text)
            tts.save("temp.mp3")
            os.system("start temp.mp3")  # For Windows
        except Exception as fallback_err:
            st.error(f"❌ Fallback TTS also failed: {fallback_err}")

# ----------- Streamlit UI --------------------------
st.title("🤖 AI Teacher Bot")
st.subheader("An AI-powered assistant for students!")

student_data = load_student_data()
student_name = st.text_input("Enter your name:")

if student_name:
    avg_marks = calculate_average(student_name, student_data)
    if avg_marks is not None:
        feedback = f"Hello {student_name}, your average score is {avg_marks:.2f}. Keep learning and improving!"
    else:
        feedback = f"Hello {student_name}, I couldn't find your records. Keep working hard!"

    st.success(feedback)
    speak(feedback)

    if st.checkbox("Do you have any doubts?"):
        question = st.text_area("What is your doubt?")
        if st.button("Ask AI"):
            if question.strip():
                answer = get_gemini_answer(question)
                st.info(answer)
                speak(answer)
            else:
                st.warning("Please enter a valid question.")

# ----------- Initialize AIRobot Singleton -----------
if 'air_robot' not in st.session_state:
    st.session_state.air_robot = AIRobot()
import json
import streamlit as st
import pyttsx3
from gtts import gTTS
import os
import google.generativeai as genai
from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase

# Configure Panda3D to run in headless mode
loadPrcFileData("", "window-type none")  # Prevents window creation
loadPrcFileData("", "audio-library-name null")  # Disables sound

# Configure Gemini AI
GEMINI_API_KEY = "AIzaSyCJ6a-YymLZ0RQUpO87JVTbtWcBnBixO88"
genai.configure(api_key=GEMINI_API_KEY)

# ----------- Singleton Wrapper for AIRobot -------------
class AIRobot(ShowBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIRobot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            super().__init__()
            self.initialized = True
            print("✅ Panda3D running in headless mode")

# ----------- Student Data Handling -----------------
def load_student_data(filename="students.json"):
    """Loads student data from a JSON file."""
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error loading student data: {e}")
        return []

def calculate_average(student_name, student_data):
    """Calculates the average marks for a student."""
    student = next((s for s in student_data if s["name"].lower() == student_name.lower()), None)
    if student:
        marks = list(student.get("subjects", {}).values())
        return sum(marks) / len(marks) if marks else None
    return None

# ----------- AI Response + Voice -------------------
def get_gemini_answer(question):
    """Fetches an answer from Gemini AI."""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-001")
        response = model.generate_content(question)
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        return f"Error fetching answer: {e}"

def speak(text):
    """Converts text to speech."""
    try:
        engine = pyttsx3.init(driverName='sapi5')  # Use Windows speech engine
        engine.say(text)
        engine.runAndWait()
    except Exception:
        try:
            tts = gTTS(text)
            tts.save("temp.mp3")
            os.system("start temp.mp3")  # Windows
        except Exception as e:
            st.error(f"❌ Text-to-speech failed: {e}")

# ----------- Streamlit UI --------------------------
st.title("🤖 AI Teacher Bot")
st.subheader("An AI-powered assistant for students!")

student_data = load_student_data()
student_name = st.text_input("Enter your name:")

if student_name:
    avg_marks = calculate_average(student_name, student_data)
    feedback = (f"Hello {student_name}, your average score is {avg_marks:.2f}. Keep learning and improving!"
                if avg_marks is not None else 
                f"Hello {student_name}, I couldn't find your records. Keep working hard!")
    
    st.success(feedback)
    speak(feedback)

    if st.checkbox("Do you have any doubts?"):
        question = st.text_area("What is your doubt?")
        if st.button("Ask AI") and question.strip():
            answer = get_gemini_answer(question)
            st.info(answer)
            speak(answer)

# ----------- Initialize AIRobot Singleton -----------
if "air_robot" not in st.session_state:
    try:
        st.session_state.air_robot = AIRobot()
    except Exception as e:
        st.error(f"❌ Failed to initialize AI Robot: {e}")
