import fitz  # PyMuPDF
import os

# 🔹 Define the folder where your PDFs are saved (Update this if needed)
pdf_folder = os.path.expanduser("~/Desktop")

# 🔹 List of Abaqus PDFs to process
pdf_files = [
    "MATERIALS.pdf",
    "EXAMPLES.pdf",
    "SCRIPTINGREFERENCE.pdf",
    "SCRIPTING.pdf",
    "KEYWORDS.pdf",
    "CAE.pdf"
]

# 🔹 Create an output folder on Desktop
output_folder = os.path.join(pdf_folder, "Extracted_Abaqus_Text")
os.makedirs(output_folder, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extract text from a given PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# 🔹 Loop through each PDF and extract text
for pdf_name in pdf_files:
    pdf_path = os.path.join(pdf_folder, pdf_name)

    # ✅ Check if the PDF exists before processing
    if os.path.exists(pdf_path):
        print(f"📖 Extracting text from: {pdf_name} ...")
        text = extract_text_from_pdf(pdf_path)

        # 🔹 Save the extracted text as a .txt file
        output_file = os.path.join(output_folder, pdf_name.replace(".pdf", ".txt"))
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ Saved extracted text: {output_file}")
    else:
        print(f"❌ File not found: {pdf_name}")

print("🚀 All PDFs processed successfully!")

