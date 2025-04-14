import streamlit as st
import pandas as pd
import json
import utils.common as com
from utils.resume_extractor import resume_extractor
from utils.pinecone_database import PineconeDatabase
from match_alogorithm.calculate_match_score import calculate_match_score

@st.cache_data
def read_city_state_data():
    data = pd.read_csv('./data/uscities.txt', sep='\t')
    if "city" in data.columns and "state_name" in data.columns:
        # Create a list of strings in the format "City, State"
        city_state_list = [f"{row['city']}, {row['state_id']}" for _, row in data.iterrows()]
        city_state_list.insert(0, "")
    else:
        city_state_list = [""]

    return city_state_list

@st.cache_resource
def retrievePineconeIndex():
    pc = PineconeDatabase(st.secrets.pinecone.api_key, st.secrets.pinecone.index_name, st.secrets.pinecone.aws_region, st.secrets.pinecone.sagemaker_endpoint)
    pc.connect_to_pinecone()
    return pc

@st.cache_resource
def retrieveOpenAIClient():
    print("calling retrieveOpenAIClient")
    return resume_extractor(st.secrets.openai.api_key)

# Streamlit app
def main():
        # add tab title
    st.set_page_config(page_title="MIRRA Matcher", layout="wide")
    com.includeCss(st, 'mirra.css')
    com.logger('Start MIRRA Matcher')
    cities_states = read_city_state_data()
    pc = retrievePineconeIndex()
    client = retrieveOpenAIClient()
    if 'resume_filename' not in st.session_state:
        st.session_state['resume_filename'] = ''
    if "disabled" not in st.session_state:
        st.session_state["disabled"] = False
    # add layout
    header = st.container(key='header')
    uploader = st.container(key='uploader')
    filter = st.form(key='filter')
    filter_dict = {}
    footer = st.container(key='footer')

    # add header
    with header:
        header.markdown(com.backgroundImage('st-key-header', 'banner.png'), unsafe_allow_html=True)
        logo, banner, team, profile = header.columns([2, 12, 1, 1])
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
        _, file_center, _ = uploader.columns([1, 4, 1])
        pdf_file = file_center.file_uploader("Finding your new job starts here.", type="pdf", key='pdf-uploader')

    def retrieve_resume_in_json(text):
        extracted_json = client.process_resume_to_json(text)
        st.session_state['resume_json'] = extracted_json
        com.logger(st.session_state['resume_json'])
    
    if pdf_file is not None and st.session_state['resume_filename'] != pdf_file.name:
        print("start resume extraction...")
        if 'resume_json' in st.session_state:
            del st.session_state['resume_json']
        st.session_state['resume_filename'] = pdf_file.name
        extracted_text = com.extract_text_from_pdf(pdf_file)
        if st.secrets.main.demo:
            com.logger("### Demo resume...")
            st.session_state['resume_json'] = com.read_json_result('resume.json')
        else:
            retrieve_resume_in_json(extracted_text)
        # task_thread = threading.Thread(target=retrieve_resume_in_json, args=(extracted_text,))
        # task_thread.start()
        # task_thread.join()
        st.session_state["disabled"] = False

    with filter:
        filter.markdown('<div class="filter-description">Set Your Filters, Then Click \'Start Match\' to Discover Your Best-Fit Roles.</div>', unsafe_allow_html=True)
        left, middle, right = st.columns([1,1,1])

    with left:
        keywords = left.text_input('Job Title: ', disabled=st.session_state.disabled)
        exp_level = left.selectbox("Experience Level:", ('', 'Internship', 'Entry-level', 'Associate', 'Senior',  'Director'), disabled=st.session_state.disabled)
        post_dt = left.selectbox("Date Posted:", ('', "Last 24 hours", "Past Week", "Past Month"), disabled=st.session_state.disabled) 

    with middle:
        location = middle.selectbox('Location: ', cities_states, disabled=st.session_state.disabled)
        domain = middle.selectbox("Industry or Domain:", ('', "Agriculture", "Education", "Finance", "Healthcare", "Information Technology", "Manufacturing", "Marketing", "Retail", "Other"), disabled=st.session_state.disabled)
        visa_sponsor = middle.radio('Visa Sponsorship:', ('Yes', 'No'), index=None, horizontal=True, key="visa_sponsor", disabled=st.session_state.disabled)

    with right:
        emp_type = right.selectbox("Employment Type:", ('', "Full-time", "Part-time", "Contract"), disabled=st.session_state.disabled)
        salary_range_from, salary_range_to = right.slider("Salary Range:", 50000, 500000, value=(50000, 50000), disabled=st.session_state.disabled)
    
    if emp_type:
        filter_dict['emp_type'] = {'$eq': emp_type}
    if post_dt:
        filter_dict['post_dt'] = {'$eq': post_dt}        
    if exp_level:
        filter_dict['exp_level'] = {'$eq': exp_level}        
    if domain:
        filter_dict['domain'] = {'$eq': domain}        
    if location:
        filter_dict['location'] = {'$eq': location + ", US"} 
    if salary_range_from and salary_range_from != salary_range_to:
        filter_dict['salary_range_from'] = {'$gte': salary_range_from}        
    if salary_range_to and salary_range_from != salary_range_to:
        filter_dict['salary_range_to'] = {'$lte': salary_range_to}        
    if visa_sponsor:
        filter_dict['visa_sponsor'] = {'$eq': visa_sponsor}

    with middle:
        if(middle.form_submit_button("Start Match", disabled=st.session_state.disabled)):
            if 'resume_json' in st.session_state:

                # Display the loading animation
                with st.spinner("Looking for the best matches... Please wait!"):

                    com.logger(filter_dict)
                    if st.secrets.pinecone.in_use:
                        response = pc.search(keywords, filter_dict)
                    else:
                        response = ""
                    # response = json.loads(vdb_result)
                    if st.secrets.aws.bucket_name:
                        job_list = com.find_record_by_ids_from_s3(response, st.secrets.aws.bucket_name, st.secrets.aws.file_key)
                    else:
                        com.logger("### Loading posting files...")    
                        job_list = com.find_record_by_ids(response, st.secrets.aws.path)
                    # print(json.dumps(job_list))
                    resume = st.session_state['resume_json']
                    com.logger(type(job_list))
                    com.logger(type(resume))
                    if st.secrets.main.demo:
                        matches = com.read_json_result('match_result.json')
                    else:
                        matches = calculate_match_score(job_desc_json_lst=job_list, candidate_resume_JSON=resume, parallel_processing=True)
                    com.logger(type(matches))
                    com.logger(len(matches))
                    if matches:
                        matches = json.dumps(matches)
                        st.session_state['matches'] = matches
                        st.switch_page("pages/match.py")
            else:
                print("Resume is not ready")

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)
    st.session_state["disabled"] = True

if __name__ == "__main__":
    main()

