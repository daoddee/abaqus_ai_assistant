import streamlit as st
import requests

# Streamlit UI
st.set_page_config(page_title="Abaqus AI Assistant", layout="wide")
st.title("🔧 Abaqus AI Assistant")
st.write("Enter a description of the simulation you want to generate.")

# User input
user_prompt = st.text_area("📝 Describe your simulation:", height=150)

if st.button("🚀 Generate Script"):
    if user_prompt.strip():
        with st.spinner("Generating Abaqus script... Please wait ⏳"):
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/generate_script",
                    json={"prompt": user_prompt}
                )

                if response.status_code == 200:
                    script = response.json().get("script", "⚠️ No script generated.")
                    st.subheader("📜 Generated Abaqus Script:")
                    st.code(script, language="python")
                else:
                    st.error("❌ Failed to generate script. Please try again.")

            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a simulation description.")

