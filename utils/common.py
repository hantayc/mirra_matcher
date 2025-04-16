import boto3
from pathlib import Path
import pandas as pd
import base64
import os
from io import BytesIO
import sys
import fitz  # PyMuPDF
import json
import streamlit as st

home_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 
def includeCss(st, filename):
    css = Path(f'./css/{filename}').read_text()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def img_to_bytes(img_name):
    img_bytes = Path(f'{home_directory}/images/{img_name}').read_bytes()
    return base64.b64encode(img_bytes).decode()

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

def loadFont():
    return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700;800;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Darker+Grotesque:wght@300;400;500;600;700;800;900&display=swap'); 
        </style>
        """
def logger(msg):
    os.write(1,f"{msg}\n".encode('utf-8'))

def find_record_by_ids(vdb_list, file_path):
    df = pd.read_excel(file_path)

    job_list = json.loads('[]')
    
    if vdb_list:
        for job in vdb_list:
            job_id = job['id']
            extracted, web_url, post_dt = find_record_by_id(job_id[4:], df)
            if extracted:
                post_json = json.loads(extracted)
                post_json['job_id'] = job_id
                post_json['web_url'] = web_url
                post_json['posted_date'] = post_dt
                job_list.append(post_json)
    else:
        job_list = get_all_records(df)

    return job_list

def get_all_records(df):
    job_list = json.loads('[]')

    for index, row in df.iterrows():
        post_json = json.loads(row['extracted_cleaned'].replace("True", "true").replace("False", "false"))
        post_json['job_id'] = f"job_{row['id']}"
        post_json['web_url'] = row['web_url']
        post_json['posted_date'] = row['posted_date'].dt.strftime('%m/%d/%Y')
        job_list.append(post_json)

    return job_list

def safe_json_loads(val):
    try:
        return json.loads(val)
    except json.JSONDecodeError:
        print(f"Error parsing JSON: {val}")
        return None

def read_excel_from_s3(bucket, key):
    """
    Helper function that reads an Excel file from S3 into a Pandas DataFrame.
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", st.secrets["aws"]["access_key_id"]),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", st.secrets["aws"]["secret_access_key"])
    )
    response = s3.get_object(Bucket=bucket, Key=key)
    # response['Body'] is a stream; wrap it with BytesIO before passing to pandas
    return pd.read_excel(BytesIO(response['Body'].read()))

def find_record_by_ids_from_s3(vdb_list, bucket, key):
    df = read_excel_from_s3(bucket, key)

    job_list = json.loads('[]')

    if vdb_list:    
        for job in vdb_list:
            job_id = job['id']
            extracted, web_url, post_dt = find_record_by_id(job_id[4:], df)
            if extracted:
                post_json = json.loads(extracted)
                post_json['job_id'] = job_id
                post_json['web_url'] = web_url
                post_json['posted_date'] = post_dt
                job_list.append(post_json)
    else:
        job_list = get_all_records(df)

    return job_list

def find_record_by_id(target_id, df):
    """
    Finds a record by ID in a given DataFrame.

    Args:
        target_id: The ID to search for.
        df (pandas.DataFrame): The DataFrame containing the data.

    Returns:
        tuple or None: A tuple containing 'extracted_cleaned', 'web_url', and 'posted_date' 
        if the record is found; otherwise, None.
    """
    # Filter the DataFrame for the record with the matching ID
    record = df[df['id'] == target_id]

    # If the record is empty, return None
    if record.empty:
        return None

    # Extract the first record (in case there are duplicates)
    record = record.iloc[0]

    # Handle NaT values in 'posted_date'
    if pd.isna(record['posted_date']):
        posted_date = None  # Or you can return a default value like 'Unknown'
    else:
        posted_date = pd.to_datetime(record['posted_date']).strftime('%m/%d/%Y')

    # Clean up the 'extracted_cleaned' value
    extracted_cleaned = record['extracted_cleaned'].replace("True", "true").replace("False", "false")

    # Return the desired values
    return extracted_cleaned, record['web_url'], posted_date
    
def getJob(job, isSelected):
    details = job["details"]
    if isSelected:
        sel_class = "selected"
    else:
        sel_class = ""
    job_html = f"""<div class="job-row {sel_class}" selected={isSelected}><a href="match?a={job['job_id']}" target="_self" class="job-detail-link">
            <div class="job-title">{'<br>'.join(details['job_title_base'])}</div>
            <div class="job-company">at {'<br>'.join(details['company_name'])}</div>
            <div class="job-location">Location: {'<br>'.join([location['city'] + ", " + location['state'] for location in details['location']])}</div>
            <div class="job-scores">Overall Scores: {job['match_scores']['overall_score']*100:.0f}%</div></a></div>
    """
    logger(job_html)

    return job_html

def find_record_by_jobid(json_data, job_id):
    """
    Finds a record in a JSON-like data structure where a specified key has a specific value.

    Args:
        json_data: The JSON data (dict or list) to search within.
        job_id: The value that the key should have for a match.

    Returns:
        The record (dict) if found, otherwise None.
    """
    for item in json_data:
        if item["job_id"] == job_id:
            return item
    return None

def include_js_file(js_file_path, post_js):
    with open('./js/' + js_file_path, 'r') as f:
        js_code = f.read()

    html_code = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <script>
                    {js_code}

                    {post_js}
                </script>
            </head>
            <body>
            </body>
        </html>
        """
    return html_code

def read_json_result(file_name):
    with open('./data/' + file_name, 'r') as f:
        json_result = f.read()
    
    return json.loads(json_result)
