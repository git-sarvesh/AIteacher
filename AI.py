import json
from direct.showbase.ShowBase import ShowBase
from panda3d.core import PointLight, AmbientLight
import pyttsx3
import google.generativeai as genai

# Configure Gemini AI
GEMINI_API_KEY = "AIzaSyCJ6a-YymLZ0RQUpO87JVTbtWcBnBixO88"
genai.configure(api_key=GEMINI_API_KEY)

class AIRobot(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Load the 3D robot model (Ensure a valid .glb, .obj, or .bam file)
        self.robot = self.loader.loadModel("robot_model.glb")  
        self.robot.reparentTo(self.render)
        self.robot.setScale(2)
        self.robot.setPos(0, 10, 0)
        
        # Add lighting
        self.setupLights()
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        
        # Load student data from JSON
        self.student_data = self.load_student_data()

        # Ask for student name and feedback
        self.get_student_feedback()

    def setupLights(self):
        """Setup ambient and point lighting."""
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((0.5, 0.5, 0.5, 1))
        self.render.setLight(self.render.attachNewNode(ambientLight))
        
        pointLight = PointLight("pointLight")
        pointLight.setColor((1, 1, 1, 1))
        pointLightNode = self.render.attachNewNode(pointLight)
        pointLightNode.setPos(5, -5, 10)
        self.render.setLight(pointLightNode)

    def load_student_data(self):
        """Load student data from JSON file."""
        try:
            with open("students.json", "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading student data: {e}")
            return []

    def speak(self, text):
        """Makes the robot speak and move its mouth."""
        print("🤖 AI says:", text)
        
        self.robot.setHpr(10, 0, 0)  # Slight head tilt while speaking
        self.engine.say(text)
        self.engine.runAndWait()
        self.robot.setHpr(0, 0, 0)  # Reset position
    
    def calculate_average(self, student_name):
        """Calculate the average marks of a student from JSON data."""
        for student in self.student_data:
            if student["name"].lower() == student_name.lower():
                marks = list(student["subjects"].values())  # Extract subject scores
                avg_marks = sum(marks) / len(marks)
                return avg_marks
        return None

    def get_gemini_answer(self, question):
        """Fetches answer from Gemini AI with improved error handling."""
        try:
            model = genai.GenerativeModel("models/gemini-1.5-flash-001")
            response = model.generate_content(question)

            # Check if response is valid
            if response and response.candidates:
                if response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text.strip()
            
            return "Sorry, I couldn't generate an appropriate response. Try rephrasing your question."
        
        except Exception as e:
            return f"Error fetching answer: {e}"

    def get_student_feedback(self):
        """Ask for student name and provide feedback."""
        student_name = input("Enter your name: ").strip()
        
        avg_marks = self.calculate_average(student_name)
        if avg_marks is not None:
            feedback = f"Hello {student_name}, your average score is {avg_marks:.2f}. Keep learning and improving!"
        else:
            feedback = f"Hello {student_name}, I couldn't find your records. Keep working hard!"
        
        self.speak(feedback)
        
        if input("Do you have any doubts? (yes/no): ").strip().lower() == "yes":
            question = input("What is your doubt? ")
            answer = self.get_gemini_answer(question)
            self.speak(answer)
        else:
            self.speak("Great! Have a wonderful day!")

if __name__ == "__main__":
    app = AIRobot()
    app.run()
