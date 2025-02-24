import os
import sqlite3
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai

# ✅ Load OpenAI API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Missing OpenAI API key. Please check your .env file.")

client = openai.OpenAI(api_key=api_key)

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Setup SQLite Database for Debugging Logs
DB_PATH = "errors.db"

def init_db():
    """Creates a database for logging errors and fixes."""
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

init_db()

# ✅ Improved AI Interaction for Abaqus
@app.route('/interactive_abaqus', methods=['POST'])
def interactive_abaqus():
    """
    Takes user command (e.g., "Create a cube 5m x 5m") and translates it into Abaqus Python code.
    """
    try:
        data = request.get_json()
        if not data or "command" not in data:
            return jsonify({"error": "❌ Invalid request. Missing 'command' field"}), 400

        user_command = data["command"]
        
        # ✅ AI Generates the Abaqus Code
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 
                    "**You are an Abaqus scripting AI.**\n"
                    "- Convert user requests into **fully functional Abaqus scripts**.\n"
                    "- Ensure correct syntax, imports, and boundary conditions.\n"
                    "- Do NOT assume missing details. Instead, **ask for clarification**."},
                {"role": "user", "content": f"Command: {user_command}"}
            ]
        )

        script_output = response.choices[0].message.content.strip()

        # ✅ Store script for debugging
        with open("last_generated_script.py", "w", encoding="utf-8") as script_file:
            script_file.write(script_output)

        return jsonify({"script": script_output})

    except Exception as e:
        return jsonify({"error": f"❌ Failed to process command: {str(e)}"}), 500

# ✅ Enhanced Abaqus Debugging API
@app.route('/debug_log', methods=['POST'])
def debug_log():
    """
    Handles Abaqus script error debugging.
    Retrieves the last generated script for improved fixes.
    """
    try:
        data = request.get_json()
        if not data or "error_log" not in data:
            return jsonify({"error": "❌ Missing 'error_log' field"}), 400

        error_log = data["error_log"].strip()
        
        # ✅ Retrieve last generated script
        script_code = open("last_generated_script.py", "r", encoding="utf-8").read()

        # ✅ AI Debugging Process
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content":
                    "**You are an Abaqus debugging assistant.**\n"
                    "- Analyze the provided error log and script.\n"
                    "- Identify **specific line(s)** causing issues.\n"
                    "- If it's a small fix, provide **corrected lines only**.\n"
                    "- If a large fix is required, provide **a fully corrected script**."},
                {"role": "user", "content": f"Error Log:\n{error_log}\n\nScript:\n{script_code}"}
            ]
        )

        debugging_tips = response.choices[0].message.content.strip()
        
        return jsonify({"debugging_tips": debugging_tips})

    except Exception as e:
        return jsonify({"error": f"❌ Failed to process error log: {str(e)}"}), 500

# ✅ Run Flask API
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)

