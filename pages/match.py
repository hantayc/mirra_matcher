import streamlit as st
import json
import utils.common as com

def join_array(array, column='', delim=','):
    return delim.join(item[column] for item in array)

# Streamlit app
def main():
    matches = json.loads('[]')
    if 'matches' in st.session_state:
        matches = st.session_state['matches']
    st.set_page_config(page_title="MIRRA Matcher - Match Results", layout="wide")
    st.markdown(com.loadFont(), unsafe_allow_html=True)
    com.includeCss(st, 'mirra.css')

    header = st.container(key='match-header')
    _, middle, _ = st.columns([1,2,1])
    footer = st.container(key='footer')

    with header:
        header.markdown(com.backgroundImage('st-key-match-header', 'match.png'), unsafe_allow_html=True)
        header.title("Your Match Is Ready!")
        header.text('See below for results')

    with middle:
        middle_container = middle.container(key="match-middle-container")
        middle_container.title("Match Results")
        
        if matches:
            middle_container.text("Results are listed from highest match to lowest match. Continue down the list for additional results.")
            no_matches = len(matches)
            if 'start_index' in st.session_state:
                start_index = st.session_state['start_index']
            else:
                start_index = 0

            for index in range(start_index, min(no_matches, 5)):
                details = matches[index]["details"]
                score = matches[index]["match_scores"]
                middle_container.subheader(f"{', '.join(details['job_title_base'])} at {', '.join(details['company_name'])}")
                if score["overall_score"]:
                    middle_container.markdown(f'<div class="overall_score_header">Overall = {score["overall_score"]*100:.0f}%</div>', unsafe_allow_html=True)
                if score["overall_skills"]:
                    middle_container.markdown(f'<li class="score_item">Skill Score: {score["overall_skills"]*100:.0f}%</li>', unsafe_allow_html=True)
                if score["overall_background"]:
                    middle_container.markdown(f'<li class="score_item">Background Score: {score["overall_background"]*100:.0f}%</li>', unsafe_allow_html=True)
                if score["overall_education"]:
                    middle_container.markdown(f'<li class="score_item">Education Score: {score["overall_education"]*100:.0f}%</li>', unsafe_allow_html=True)
                if score["overall_credentials"]:
                    middle_container.markdown(f'<li class="score_item">Credentials Score: {score["overall_credentials"]*100:.0f}%</li>', unsafe_allow_html=True)

                match_left, match_middle, match_right = middle_container.columns([1,1,1])
                with match_left:
                    if score["overall_mandatory"]:
                        match_left.markdown(f'<div class="score_header">Mandatory = {score["overall_mandatory"]*100:.0f}%</div>', unsafe_allow_html=True)
                    if score["mandatory_skill_score"]:
                        match_left.markdown(f'<li class="score_item">Skill Score: {score["mandatory_skill_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_background_score"]:
                        match_left.markdown(f'<li class="score_item">Background Score: {score["mandatory_background_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_education_score"]:
                        match_left.markdown(f'<li class="score_item">Education Score: {score["mandatory_education_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_industry_score"]:
                        match_left.markdown(f'<li class="score_item">Indurstry Score: {score["mandatory_industry_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_credentials_score"]:
                        match_left.markdown(f'<li class="score_item">Credentials Score: {score["mandatory_credentials_score"]*100:.0f}%</li>', unsafe_allow_html=True)

                with match_middle:
                    if score["overall_preferred"]:
                        match_middle.markdown(f'<div class="score_header">Preferred = {score["overall_preferred"]*100:.0f}%</div>', unsafe_allow_html=True)
                    if score["preferred_skill_score"]:
                        match_middle.markdown(f'<li class="score_item">Skill Score: {score["preferred_skill_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_background_score"]:
                        match_middle.markdown(f'<li class="score_item">Background Score: {score["preferred_background_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_education_score"]:
                        match_middle.markdown(f'<li class="score_item">Education Score: {score["preferred_education_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_industry_score"]:
                        match_middle.markdown(f'<li class="score_item">Indurstry Score: {score["preferred_industry_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_credentials_score"]:
                        match_middle.markdown(f'<li class="score_item">Credentials Score: {score["preferred_credentials_score"]*100:.0f}%</li>', unsafe_allow_html=True)

                with match_right:
                    if score["responsibilities_score"]:
                        match_right.markdown(f'<div class="score_header">Responsibilites = {score["responsibilities_score"]*100:.0f}%</div>', unsafe_allow_html=True)

                middle_container.markdown(f'<div id="job-location"><span id="location-label">Location:</span> {"<br>".join(item["city"] + ", " + item["state"] for item in details["location"])}</div>', unsafe_allow_html=True)
        else:
            middle_container.text("We couldn’t find any jobs matching your search criteria at the moment. Don’t worry! Try adjusting your filters or check back later for new opportunities. Your next great job is just around the corner!")

        bottom_container = middle_container.container(key='bottom-container')
        if(bottom_container.button("Re-Run and Adjust Filters")):
            st.switch_page("app.py")

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()