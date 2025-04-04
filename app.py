import streamlit as st
import pandas as pd
import json
import asyncio
import utils.common as com
from utils.resume_extractor import resume_extractor
from utils.pinecone_database import PineconeDatabase
# from match_alogorithm.calculate_match_score import calculate_match_score

model_path = "./llama_8B_test"

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

async def extract_resume(extracted_text):
    st.session_state['resume_ready'] = False
    openai = retrieveOpenAIClient()
    json_result = openai.process_resume_to_json(extracted_text)
    st.session_state['resume'] = json_result
    st.session_state['resume_ready'] = True

@st.dialog("Resume is currently process")
def resume_not_ready():
    st.write("Please wait few seconds and search it again.")
    if st.button("Ok"):
        st.rerun()

# Streamlit app
def main():
        # add tab title
    st.set_page_config(page_title="MIRRA Matcher", layout="wide")
    
    cities_states = read_city_state_data()
    # pc, index = retrievePineconeIndex()

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
        asyncio.run(extract_resume(extracted_text))
        extracted_json = json.loads("""{"skills":[{"skill":[["spearheaded cross-functional teams","deliver complex technical projects"]],"years":0.08},{"skill":[["data lake development","implementation"]],"years":0},{"skill":[["database administration"]],"years":0},{"skill":[["database management"]],"years":0},{"skill":[["data governance"]],"years":0},{"skill":[["data compliance"]],"years":0},{"skill":[["data cleaning"]],"years":0},{"skill":[["data preparation"]],"years":0},{"skill":[["data warehousing"]],"years":0},{"skill":[["business intelligence"]],"years":0},{"skill":[["analytics"]],"years":0},{"skill":[["cloud computing"]],"years":0},{"skill":[["data visualization"]],"years":0},{"skill":[["project management"]],"years":0},{"skill":[["ETL"]],"years":0},{"skill":[["visualization"]],"years":0},{"skill":[["reporting"]],"years":0},{"skill":[["big data"]],"years":0},{"skill":[["machine learning"]],"years":0},{"skill":[["artificial intelligence"]],"years":0},{"skill":[["AWS Service APIs"]],"years":0},{"skill":[["containers"]],"years":0},{"skill":[["CI/CD Pipeline"]],"years":0},{"skill":[["forecasting algorithms"]],"years":0},{"skill":[["Google Cloud Healthcare API"]],"years":0},{"skill":[["Keras"]],"years":0},{"skill":[["PyTorch Libraries"]],"years":0},{"skill":[["neural networks"]],"years":0},{"skill":[["detect labels"]],"years":0},{"skill":[["detect images"]],"years":0},{"skill":[["detect text files"]],"years":0},{"skill":[["image processing"]],"years":0},{"skill":[["Kinesis"]],"years":0},{"skill":[["Pyspark Library"]],"years":0},{"skill":[["Jupyter Notebook"]],"years":0},{"skill":[["chatbot development"]],"years":0},{"skill":[["edge device integration","machine learning platforms"]],"years":0},{"skill":[["SQL"]],"years":0},{"skill":[["NoSQL"]],"years":0},{"skill":[["ElastiCache"]],"years":0},{"skill":[["RDS"]],"years":0},{"skill":[["Redis"]],"years":0},{"skill":[["AWS Athena"]],"years":0},{"skill":[["Aurora"]],"years":0},{"skill":[["DynamoDB"]],"years":0},{"skill":[["DevOps"]],"years":0},{"skill":[["Splunk"]],"years":0},{"skill":[["EC2 Storage"]],"years":0},{"skill":[["Elastic Load Balancing"]],"years":0},{"skill":[["Application Auto Scaling"]],"years":0},{"skill":[["Route 53"]],"years":0},{"skill":[["CloudFront"]],"years":0},{"skill":[["ECS"]],"years":0},{"skill":[["ECR"]],"years":0},{"skill":[["Fargate"]],"years":0},{"skill":[["Docker"]],"years":0},{"skill":[["CodeCommit"]],"years":0},{"skill":[["CodePipeline"]],"years":0},{"skill":[["CodeDeploy"]],"years":0},{"skill":[["X-Ray"]],"years":0},{"skill":[["CloudWatch"]],"years":0},{"skill":[["SQS"]],"years":0},{"skill":[["SNS"]],"years":0},{"skill":[["AWS Serverless API"]],"years":0},{"skill":[["Cognito"]],"years":0},{"skill":[["AppSync"]],"years":0},{"skill":[["Python"]],"years":0},{"skill":[["PowerShell"]],"years":0},{"skill":[["innovative thinking"]],"years":0},{"skill":[["organizational skills"]],"years":0},{"skill":[["strong analytical skills"]],"years":0},{"skill":[["project management"]],"years":0},{"skill":[["data analysis"]],"years":0},{"skill":[["effective communication"]],"years":0},{"skill":[["cross-functional collaboration"]],"years":0},{"skill":[["attention to detail"]],"years":0},{"skill":[["time management"]],"years":0},{"skill":[["interpersonal skills"]],"years":0},{"skill":[["problem-solving abilities"]],"years":0},{"skill":[["expertise in subject matter"]],"years":0},{"skill":[["industry knowledge"]],"years":0},{"skill":[["adaptability"]],"years":0},{"skill":[["flexibility"]],"years":0},{"skill":[["team leadership"]],"years":0},{"skill":[["disaster recovery planning"]],"years":0},{"skill":[["self-awareness"]],"years":0},{"skill":[["emotional intelligence"]],"years":0},{"skill":[["resilience building"]],"years":0},{"skill":[["active listening"]],"years":0},{"skill":[["conflict resolution"]],"years":0},{"skill":[["growth mindset"]],"years":0}],"education":[{"gpa":0,"major":["Data Science"],"minor":[],"institution":"North Central University","education_level":"Doctoral's"}],"credentials":[{"credential":["AWS Machine Learning"]},{"credential":["AWS Cloud Practitioner"]},{"credential":["AWS Developer Associate"]},{"credential":["PMP"]},{"credential":["CSM"]},{"credential":["ITIL"]}],"professional_background":[{"years":0.08,"industry":["Technology"],"background":["Remote Technical Program Manager","Technical Program Manager"],"related_fields_of_study":["Information Technology","Computer Science"]},{"years":4.92,"industry":[],"background":["Consultant SME","Senior Consultant"],"related_fields_of_study":["Information Technology","Computer Science"]},{"years":1.08,"industry":["Nonprofit"],"background":["Director of Interoperability"],"related_fields_of_study":["Information Technology","Computer Science"]},{"years":1.58,"industry":[],"background":["Senior Integration Architect","Integration Architect"],"related_fields_of_study":["Information Technology","Computer Science"]},{"years":1.17,"industry":[],"background":["HIM IT Analyst","IT Analyst"],"related_fields_of_study":["Information Technology","Computer Science"]},{"years":6.75,"industry":[],"background":["Business Operation Sr MGR","Senior Manager"],"related_fields_of_study":["Business","Finance"]}]}""")

    with filter:
        filter.markdown('<div class="filter-description">Set Your Filters, Then Click \'Start Match\' to Discover Your Best-Fit Roles.</div>', unsafe_allow_html=True)
        left, middle, right = st.columns([1,1,1])

    with left:
        keywords = left.text_input('Job Title (Keywords): ')
        emp_type = left.selectbox("Employment Type:", ('', "Full-time", "Part-time", "Contract", "Internship"))
        post_dt = left.selectbox("Date Posted:", ('', "Last 24 hours", "Past Week", "Past Month")) 

    with middle:
        job_title = middle.text_input('Job Title: ')
        exp_level = middle.selectbox("Experience Level:", ('', 'Entry-level', 'Mid-level', 'Senior'))
        domain = middle.selectbox("Industry or Domain:", ('', "Agriculture", "Education", "Finance", "Healthcare", "Information Technology", "Manufacturing", "Marketing", "Retail", "Other"))

    with right:
        location = right.selectbox('Location: ', cities_states)
        salary_range_from, salary_range_to = st.slider("Salary Range:", 50000, 500000, value=(50000, 50000))
        visa_sponsor = right.radio('Visa Sponsorship:', ('Yes', 'No'), index=None, horizontal=True, key="visa_sponsor")
    
    if emp_type:
        filter_dict['emp_type'] = {'$eq': emp_type}
    if post_dt:
        filter_dict['post_dt'] = {'$eq': post_dt}        
    if job_title:
        filter_dict['job_title'] = {'$eq': job_title}
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
            if st.session_state['resume_ready']:
            # if index:
                # response = pc.search(index, keywords, filter_dict)
                # matches = calculate_match_score(json.loads(response), extracted_json)
                matches = """[{"details": {"wage": [],
   "benefits": {"fsa": false,
    "hsa": false,
    "bonus": false,
    "other": [],
    "dental": false,
    "equity": false,
    "vision": false,
    "medical": false,
    "401k_match": false,
    "mental_health": false,
    "unlimited_pto": false,
    "tuition_reimbursement": false},
   "location": [{"city": "Windsor", "state": "CT", "country": "US"}],
   "job_title": ["Salesforce Business Analyst with SCM/ logistics domain Experience"],
   "tax_terms": ["Direct-hire contract",
    "Contract Corp-to-Corp",
    "Contract W2",
    "Full-time"],
   "wfh_policy": ["Onsite"],
   "company_name": ["Techgene"],
   "company_stage": [],
   "work_schedule": [],
   "job_title_base": ["Salesforce Business Analyst"],
   "employment_type": [],
   "travel_required": {"required": false, "hours_weekly": 0},
   "company_industry": [],
   "experience_level": [],
   "work_authorization": []},
  "mandatory": {"education": [],
   "credentials": [],
   "hard_skills": [{"skill": [["Business Analyst"]], "minyears": [5]},
    {"skill": [["Microsoft Office Suite"]], "minyears": [0]},
    {"skill": [["Word"]], "minyears": [0]},
    {"skill": [["Excel"]], "minyears": [0]},
    {"skill": [["PowerPoint"]], "minyears": [0]},
    {"skill": [["Data analysis tools"], ["SQL"], ["Tableau"]],
     "minyears": [0]}],
   "professional_background": [{"industry": ["SCM", "logistics"],
     "minyears": [0],
     "background": [["Business Analyst"]]}]},
  "preferred": {"education": [],
   "credentials": [],
   "hard_skills": [{"skill": [["Project management methodologies"],
      ["Agile"],
      ["Waterfall"]],
     "minyears": [0]}],
   "professional_background": []},
  "responsibility": {"hard_skills": [{"skill": [["Analyzing business challenges"]]},
    {"skill": [["designing solutions"]]},
    {"skill": [["implementing solutions"]]},
    {"skill": [["driving measurable business impact"]]}]},
  "job_id": "cbbc9bbc-2f21-451f-ac20-01e4f2c611e1",
  "match_scores": {"mandatory_background_score": 0.7051539023717246,
   "mandatory_industry_score": 0.6039732297261557,
   "preferred_background_score": "",
   "preferred_industry_score": "",
   "mandatory_education_score": "",
   "preferred_education_score": "",
   "mandatory_credentials_score": "",
   "preferred_credentials_score": "",
   "responsibilities_score": 0.7335989773273469,
   "mandatory_skill_score": 0.6934332781367835,
   "preferred_skill_score": 0.6572391192118329,
   "overall_mandatory": 0.7107287192786184,
   "overall_preferred": 0.6572391192118329,
   "overall_score": 0.6839839192452256,
   "overall_skills": 0.6753361986743082,
   "overall_education": "",
   "overall_background": 0.7051539023717246,
   "overall_credentials": ""}}]"""
                if 'matches' not in st.session_state:
                    matches = json.loads(matches)
                    st.session_state['matches'] = matches
                st.switch_page("pages/match.py")
            else:
                resume_not_ready()

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

