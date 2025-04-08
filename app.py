import streamlit as st
import pandas as pd
import json
import asyncio
import utils.common as com
from utils.resume_extractor import resume_extractor
from utils.pinecone_database import PineconeDatabase
from logging import getLogger
import os 
from match_alogorithm.calculate_match_score import calculate_match_score

@st.cache_resource
def read_city_state_data():
    data = pd.read_csv('./data/uscities.txt', sep='\t')
    if "city" in data.columns and "state_name" in data.columns:
        # Create a list of strings in the format "City, State"
        city_state_list = [f"{row['city']}, {row['state_name']}" for _, row in data.iterrows()]
        city_state_list.insert(0, "")
    else:
        city_state_list = [""]

    return city_state_list

@st.cache_resource
def retrievePineconeIndex():
    pc = PineconeDatabase(st.secrets.pinecone.api_key, st.secrets.pinecone.index_name, st.secrets.pinecone.aws_region, st.secrets.pinecone.sagemaker_endpoint)
    return pc, pc.connect_to_pinecone()

@st.cache_resource
def retrieveOpenAIClient():
    return resume_extractor(st.secrets.openai.api_key)

# Streamlit app
def main():
        # add tab title
    st.set_page_config(page_title="MIRRA Matcher", layout="wide")
    com.logger('Start MIRRA Matcher')
    cities_states = read_city_state_data()
    pc, index = retrievePineconeIndex()
    client = retrieveOpenAIClient()

    com.includeCss(st, 'mirra.css')

    # add layout
    header = st.container(key='header')
    uploader = st.container(key='uploader')
    filter = st.form(key='filter')
    filter_dict = {}
    footer = st.container(key='footer')

    # add header
    with header:
        header.markdown(com.backgroundImage('st-key-header', 'banner.png'), unsafe_allow_html=True)
        logo, banner, team, profile = header.columns([2,12,1,1])
        logo.image('./images/logo.png', width=180)
        team.page_link("pages/team.py", label="Meet My Team")
        profile.page_link("pages/login.py", label="login")
    
    with banner:
        menu = banner.container(key="menu")
        why_mirra, how_it_works, other = menu.columns([1,1,8])
        why_mirra.page_link('pages/why.py', label='Why MIRRA')
        how_it_works.page_link('pages/works.py', label='How it works')
        banner.markdown('<div class="project_name">Matching Intelligence for <span class="project_name_em">Resume & Role Alignment</span></div>', unsafe_allow_html=True)

    with uploader:
        _, file_center, _ = uploader.columns([1,4,1])
        pdf_file = file_center.file_uploader("Finding your new job starts here.", type="pdf", key='pdf-uploader')

    if pdf_file is not None:
        extracted_text = com.extract_text_from_pdf(pdf_file)
        extracted_json = client.process_resume_to_json(extracted_text)

    with filter:
        filter.markdown('<div class="filter-description">Set Your Filters, Then Click \'Start Match\' to Discover Your Best-Fit Roles.</div>', unsafe_allow_html=True)
        left, middle, right = st.columns([1,1,1])

    with left:
        keywords = left.text_input('Job Title: ')
        exp_level = middle.selectbox("Experience Level:", ('', 'Entry-level', 'Mid-level', 'Senior'))
        post_dt = left.selectbox("Date Posted:", ('', "Last 24 hours", "Past Week", "Past Month")) 

    with middle:
        location = right.selectbox('Location: ', cities_states)
        domain = middle.selectbox("Industry or Domain:", ('', "Agriculture", "Education", "Finance", "Healthcare", "Information Technology", "Manufacturing", "Marketing", "Retail", "Other"))
        visa_sponsor = right.radio('Visa Sponsorship:', ('Yes', 'No'), index=None, horizontal=True, key="visa_sponsor")

    with right:
        emp_type = left.selectbox("Employment Type:", ('', "Full-time", "Part-time", "Contract", "Internship"))
        salary_range_from, salary_range_to = st.slider("Salary Range:", 50000, 500000, value=(50000, 50000))
    
    if emp_type:
        filter_dict['emp_type'] = {'$eq': emp_type}
    if post_dt:
        filter_dict['post_dt'] = {'$eq': post_dt}        
    if exp_level:
        filter_dict['exp_level'] = {'$eq': exp_level}        
    if domain:
        filter_dict['domain'] = {'$eq': domain}        
    if location:
        filter_dict['location'] = {'$eq': location} 
    if salary_range_from and salary_range_from != salary_range_to:
        filter_dict['salary_range_from'] = {'$gte': salary_range_from}        
    if salary_range_to and salary_range_from != salary_range_to:
        filter_dict['salary_range_to'] = {'$lte': salary_range_to}        
    if visa_sponsor:
        filter_dict['visa_sponsor'] = {'$eq': visa_sponsor}

    with middle:
        if(middle.form_submit_button("Start Match")):
            # if st.session_state['resume_ready']:
            if index:
                response = pc.search(index, keywords, filter_dict)
                if st.secrets.aws.bucket_name:
                    job_list = com.read_excel_from_s3(t.secrets.aws.bucket_name, t.secrets.aws.file_key)
                else:
                    job_list = com.find_record_by_ids(response, st.secrets.aws.path)
                matches = calculate_match_score(job_list, extracted_json)

                if 'matches' not in st.session_state:
                    matches = json.loads(matches)
                    st.session_state['matches'] = matches
                st.switch_page("pages/match.py")
            # else:
            #     resume_not_ready()

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

