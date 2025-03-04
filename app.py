import streamlit as st
import utils.common as com

cities_states = com.read_city_state_data()

# Streamlit app
def main():
    # add tab title
    st.set_page_config(page_title="MIRRA Matcher", layout="wide")
    com.includeCss(st, 'mirra.css')

    # add layout
    header = st.container(key='header')
    uploader = st.container(key='uploader')
    filter = st.container(key='filter')
    filter_dict = {}
    footer = st.container()

    # add header
    with header:
        header.markdown(com.backgroundImage('st-key-header', 'banner.png'), unsafe_allow_html=True)
        logo, banner, team, profile = header.columns([2,12,1,1])
        logo.image('./images/logo.png', width=180)
        team.page_link("pages/team.py", label="Meet My Team")
        # team.markdown('<div class="meet-my-team">Meet My Team</div>', unsafe_allow_html=True)
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
    
    if keywords:
        filter_dict['keywords'] = keywords
    if emp_type:
        filter_dict['emp_type'] = emp_type        
    if post_dt:
        filter_dict['post_dt'] = post_dt        
    if job_title:
        filter_dict['job_title'] = job_title        
    if exp_level:
        filter_dict['exp_level'] = exp_level        
    if domain:
        filter_dict['domain'] = domain        
    if location:
        filter_dict['location'] = location        
    if salary_range_from:
        filter_dict['salary_range_from'] = salary_range_from        
    if salary_range_to:
        filter_dict['salary_range_to'] = salary_range_to        
    if visa_sponsor:
        filter_dict['visa_sponsor'] = visa_sponsor

    with middle:
        if(middle.button("Start Match", key="start-match")):
            # response = find_best_matches(filter_dict)
            middle.write(filter_dict)

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

