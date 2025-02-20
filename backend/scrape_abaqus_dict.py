import requests
from bs4 import BeautifulSoup
import json

# URL of the Abaqus documentation
URL = "https://classes.engineering.wustl.edu/2009/spring/mase5513/abaqus/docs/v6.6/books/ker/default.htm?startat=pt01ch12pyo03.html"

# Send a GET request to the website
response = requests.get(URL)
if response.status_code != 200:
    print("❌ Failed to retrieve the webpage")
    exit()

# Parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Extract command names and descriptions
commands = {}

# Example: Extract headings and descriptions from the HTML (adjust based on actual structure)
for section in soup.find_all("p"):
    command_name = section.find("b")  # Example: Commands might be in <b> tags
    description = section.text.strip()
    
    if command_name:
        command_text = command_name.text.strip()
        commands[command_text] = description

# Save the dictionary as a JSON file
with open("abaqus_dictionary.json", "w", encoding="utf-8") as f:
    json.dump(commands, f, indent=4, ensure_ascii=False)

print("✅ Abaqus dictionary saved successfully!")

