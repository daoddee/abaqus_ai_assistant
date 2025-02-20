import sqlite3
from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
from flask_caching import Cache

# ✅ Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Missing OpenAI API key. Please check your .env file.")
client = openai.OpenAI(api_key=api_key)

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Setup Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 600})

# ✅ Setup SQLite Database for Debug Logs
DB_PATH = "errors.db"

def init_db():
    """Create database and table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_message TEXT UNIQUE,
            ai_solution TEXT
        )
    """)
    conn.commit()
    conn.close()

# ✅ Initialize database on startup
init_db()

# ✅ Home route
@app.route('/')
def home():
    return "✅ Flask server is running!"

# ✅ Abaqus Help Chatbot API
@app.route('/abaqus_help', methods=['POST'])
def abaqus_help():
    """
    Handles user queries related to Abaqus scripting.
    """
    try:
        data = request.get_json()
        print("Received request:", data)  # Debugging line

        if not data or "query" not in data:
            return jsonify({"error": "❌ Invalid request. Missing 'query' field."}), 400

        user_query = data["query"].strip()
        
        if len(user_query) < 5:
            return jsonify({"error": "❌ Query too short. Please provide a detailed question."}), 400
        
        # Send request to OpenAI GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 
                    "You are an Abaqus scripting expert. Answer questions about Abaqus scripting, debugging, "
                    "material definitions, boundary conditions, meshing, job submission, and best practices."},
                {"role": "user", "content": user_query}
            ]
        )               

        help_response = response.choices[0].message.content.strip()
        return jsonify({"response": help_response})

    except Exception as e:
        print("Error:", str(e))  # Debugging line
        return jsonify({"error": f"❌ Failed to retrieve information: {str(e)}"}), 500

# ✅ Abaqus Script Generator API
@app.route('/generate_script', methods=['POST'])
def generate_script():
    """
    Generates an Abaqus script based on the user's request.
    Uses OpenAI's GPT-4 to verify correctness.
    """
    data = request.get_json()
    user_prompt = data.get("prompt")

    if not user_prompt:
        return jsonify({"error": "❌ No prompt provided"}), 400

    try:
        script_output = None

        # ✅ Run 3x verification to ensure valid Abaqus script
        for _ in range(3):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content":
                        "You are an Abaqus scripting expert. Generate a fully functional Abaqus Python script."
                        "Ensure correct syntax, imports, material definitions, steps, boundary conditions, meshing, and job submission."
                        "Run internal verification to check for potential errors."},
                    {"role": "user", "content": f"Simulation request: {user_prompt}"}
                ]
            )
            script_output = response.choices[0].message.content.strip()

            # ✅ Check if script is valid
            if script_output and "from abaqus" in script_output:
                break  # ✅ Valid script found

        return jsonify({"script": script_output})

    except Exception as e:
        return jsonify({"error": f"❌ Failed to generate script: {str(e)}"}), 500

# ✅ Simulation Optimization API
@app.route('/optimize_simulation', methods=['POST'])
def optimize_simulation():
    """
    Analyzes the user's Abaqus simulation and suggests optimizations.
    """
    data = request.get_json()
    user_prompt = data.get("prompt")

    if not user_prompt:
        return jsonify({"error": "❌ No prompt provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content":
                    "You are an expert in Abaqus simulation optimization. "
                    "Analyze the request and suggest improvements:\n\n"
                    "### 🔍 Problem Analysis\n"
                    "- Identify key factors affecting accuracy.\n\n"
                    "### 🛠 Solver Settings\n"
                    "- Recommend solver type and time increments.\n\n"
                    "### 📏 Mesh Optimization\n"
                    "- Suggest better mesh size and element types.\n\n"
                    "### 💡 Additional Enhancements\n"
                    "- Propose boundary condition improvements and computation time reductions."},
                {"role": "user", "content": user_prompt}
            ]
        )   

        optimization_tips = response.choices[0].message.content.strip()
        return jsonify({"optimization_tips": optimization_tips})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

