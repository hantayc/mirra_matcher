from pathlib import Path
import base64
import os
import sys
import fitz  # PyMuPDF
import pandas as pd

home_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 
def includeCss(st, filename):
    css = Path(f'./css/{filename}').read_text()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def img_to_bytes(img_name):
    img_bytes = Path(f'{home_directory}/images/{img_name}').read_bytes()
    return base64.b64encode(img_bytes).decode()

def read_city_state_data():
    data = pd.read_csv('./data/uscities.txt', sep='\t')
    if "city" in data.columns and "state_name" in data.columns:
        # Create a list of strings in the format "City, State"
        city_state_list = [f"{row['city']}, {row['state_name']}" for _, row in data.iterrows()]
        city_state_list.insert(0, "")
    else:
        city_state_list = [""]

    return city_state_list


def backgroundImage(class_name, img_name):
    return "<style>" \
            "." + class_name + " {" \
            "   background-image: url('data:image/png;base64," + img_to_bytes(img_name) + "');"  \
            "}</style>";

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Sample data
def job_data():
    return [
        {"company": "Tech Innovators Inc.", "title": "Software Engineer", "description": "Develop and maintain software applications.", "features": "Salary: $120,000\nBenefits: Health, Dental"},
        {"company": "Data Insights LLC", "title": "Data Scientist", "description": "Analyze data to provide insights.", "features": "Salary: $110,000\nBenefits: Health, Vision"},
        {"company": "Product Leaders Ltd.", "title": "Product Manager", "description": "Lead product development and strategy.", "features": "Salary: $130,000\nBenefits: Health, 401k"},
        # Add more job records as needed
    ]

def display_job_postings(st):
    html = "<table width='100%'>"
    for job in job_data():
        features = job['features'].replace('\n', '<br>')
        html += f"<tr><td class='post-header'>{job['company']} - {job['title']}</td></tr>" \
             + f"<tr><td>{job['description']}</td></tr>" \
             + f"<tr><td>{features}</td></tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

