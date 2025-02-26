import os
import subprocess
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)

# ✅ Windows Abaqus Python Path (Update if needed)
ABAQUS_PYTHON_PATH = r"C:\SIMULIA\CAE\2024LE\win_b64\code\bin\SMAPython.exe"

# ✅ Ensure Abaqus Python Exists
if not os.path.exists(ABAQUS_PYTHON_PATH):
    raise FileNotFoundError(f"❌ Abaqus Python not found at {ABAQUS_PYTHON_PATH}")

# ✅ Ping Endpoint (Test API)
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "✅ API is running successfully!"})

# ✅ Create Abaqus Object
@app.route('/create_abaqus_object', methods=['POST'])
def create_abaqus_object():
    try:
        data = request.get_json()
        object_type = data.get("object_type")

        if not object_type:
            return jsonify({"error": "❌ No object type provided"}), 400

        # ✅ Generate Abaqus Script
        abaqus_script = generate_abaqus_script(object_type)

        # ✅ Run Abaqus Script Remotely
        result = run_abaqus_script(abaqus_script)

        return jsonify({"script": abaqus_script, "output": result})

    except Exception as e:
        return jsonify({"error": f"❌ Failed to create object: {str(e)}"}), 500

# ✅ Generate Abaqus Script
def generate_abaqus_script(object_type):
    """
    Generates an Abaqus Python script to create an object.
    """
    if object_type.lower() == "cube":
        script = """
from abaqus import *
from abaqusConstants import *
session.viewports['Viewport: 1'].setValues(displayedObject=None)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0, 0), point2=(1, 1))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Cube', type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Cube'].BaseSolidExtrude(sketch=mdb.models['Model-1'].sketches['__profile__'], depth=1.0)
"""
    else:
        raise ValueError("❌ Unsupported object type")

    return script

# ✅ Run Abaqus Script on Windows Machine
def run_abaqus_script(script):
    """
    Executes an Abaqus Python script using Abaqus Python.
    """
    script_path = os.path.join(os.getcwd(), "temp_script.py")

    # ✅ Save script to file
    with open(script_path, "w") as f:
        f.write(script)

    try:
        # ✅ Run Abaqus Python
        result = subprocess.run([ABAQUS_PYTHON_PATH, script_path], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr

    except Exception as e:
        return str(e)

# ✅ Run Flask Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

