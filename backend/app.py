import os
import subprocess
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# ✅ Define Abaqus Python Path
ABAQUS_PYTHON_PATH = r"C:\SIMULIA\CAE\2024LE\win_b64\code\bin\SMAPython.exe"

# ✅ Store last generated script for debugging
generated_scripts = {"latest_script": None}


@app.route('/ping', methods=['GET'])
def ping():
    """ Check if the server is running """
    return jsonify({"message": "✅ Abaqus AI Backend is Running!"})


@app.route('/create_abaqus_object', methods=['POST'])
def create_abaqus_object():
    """
    Generates an Abaqus script, saves it, and runs it inside Abaqus automatically.
    """
    try:
        data = request.get_json()
        object_type = data.get("object_type", "").lower()

        if not object_type:
            return jsonify({"error": "❌ No object type provided"}), 400

        # ✅ Step 1: Generate the Abaqus script
        script_content = f"""
from abaqus import *
from abaqusConstants import *

session.viewports['Viewport: 1'].setValues(displayedObject=None)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0, 0), point2=(1, 1))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='{object_type.capitalize()}', type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['{object_type.capitalize()}'].BaseSolidExtrude(sketch=mdb.models['Model-1'].sketches['__profile__'], depth=1.0)
"""

        # ✅ Step 2: Save the script
        script_path = os.path.join(os.getcwd(), f"{object_type}.py")
        with open(script_path, "w", encoding="utf-8") as file:
            file.write(script_content)

        # ✅ Store script for debugging
        generated_scripts["latest_script"] = script_content

        # ✅ Step 3: Run the script inside Abaqus automatically
        process = subprocess.run([ABAQUS_PYTHON_PATH, script_path], capture_output=True, text=True)

        # ✅ Step 4: Return the script output
        return jsonify({
            "script": script_content,
            "execution_output": process.stdout,
            "execution_error": process.stderr
        })

    except Exception as e:
        return jsonify({"error": f"❌ Failed to create object: {str(e)}"}), 500


@app.route('/generate_script', methods=['POST'])
def generate_script():
    """
    Generates an Abaqus script and runs AI-based verification to check for errors.
    """
    try:
        data = request.get_json()
        user_prompt = data.get("prompt")

        if not user_prompt:
            return jsonify({"error": "❌ No prompt provided"}), 400

        script_output = None
        max_attempts = 3  # ✅ Limit retries to 3 for efficiency

        # ✅ Step 1: Generate Abaqus Script with AI Verification
        for attempt in range(max_attempts):
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content":
                            "**You are an Abaqus scripting expert.**\n"
                            "Generate a **fully functional** Python script for Abaqus that includes:\n"
                            "- Correct syntax and imports ✅\n"
                            "- Proper material definitions ✅\n"
                            "- Valid sections, loads, steps, and BCs ✅\n"
                            "- Ensure error-free execution ✅\n"
                            "- If missing parameters, prompt for them ✅\n"
                        },
                        {"role": "user", "content": f"Simulation request:\n{user_prompt}"}
                    ]
                }
            )

            script_output = response.json()["choices"][0]["message"]["content"].strip()

            if script_output and "from abaqus" in script_output:
                break  # ✅ Valid script found, stop retries

        # ❌ If no valid script was generated after 3 attempts
        if not script_output or "from abaqus" not in script_output:
            return jsonify({"error": "❌ AI failed to generate a valid script. Please refine your prompt."}), 500

        # ✅ Step 2: AI Self-Verification for Debugging
        verify_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "**You are an Abaqus code reviewer.**\n"
                        "1️⃣ Analyze the script for **syntax errors, missing parameters, and logic issues.**\n"
                        "2️⃣ Identify **invalid commands and suggest corrections.**\n"
                        "3️⃣ If corrections are needed, provide a **revised script under 'Corrected Script'.**\n"
                        "4️⃣ If **no errors are found, explicitly confirm that the script is correct.**\n"
                        "5️⃣ Ensure the corrected code runs **without modification.**"
                    },
                    {"role": "user", "content": f"Check this script for errors:\n\n{script_output}"}
                ]
            }
        )

        verification_feedback = verify_response.json()["choices"][0]["message"]["content"].strip()

        # ✅ Store script for debugging
        generated_scripts["latest_script"] = script_output

        return jsonify({"script": script_output, "verification": verification_feedback})

    except Exception as e:
        return jsonify({"error": f"❌ Failed to generate script: {str(e)}"}), 500


@app.route('/debug_log', methods=['POST'])
def debug_log():
    """
    Handles Abaqus script error debugging.
    """
    try:
        data = request.get_json()
        error_log = data.get("error_log", "").strip()

        if len(error_log) < 10:
            return jsonify({"error": "❌ Error log too short. Provide a valid error message."}), 400

        # ✅ Retrieve last generated script
        script_code = generated_scripts.get('latest_script', None)

        if not script_code:
            return jsonify({"error": "❌ No script found. Please generate a script first."}), 400

        # ✅ Send error log + full script to OpenAI for debugging
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content":
                        "You are an advanced Abaqus debugging assistant. Analyze the provided Abaqus error log and script.\n"
                        "- Clearly explain the error.\n"
                        "- Identify the specific line(s) that need fixing.\n"
                        "- Provide a corrected script if needed.\n"
                        "- Ensure the fixed code is fully functional and formatted correctly.\n"
                    },
                    {"role": "user", "content": f"Error log:\n{error_log}\n\nScript:\n{script_code}"}
                ]
            }
        )

        debugging_tips = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"debugging_tips": debugging_tips})

    except Exception as e:
        return jsonify({"error": f"❌ Failed to process error log: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

