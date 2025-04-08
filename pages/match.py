import streamlit as st
import json
import pandas as pd
import utils.common as com

def join_array(array, column='', delim=','):
    return delim.join(item[column] for item in array)

# Streamlit app
def main():
    st.set_page_config(page_title="MIRRA Matcher - Match Results", layout="wide")
    st.markdown(com.loadFont(), unsafe_allow_html=True)
    com.includeCss(st, 'match.css')

    matches = json.loads('[]')
    if 'matches' in st.session_state:
        matches = st.session_state['matches']
    com.logger(len(matches))

    if "a" in st.query_params:
        job_id = st.query_params["a"]
    elif matches:
        job_id = matches[0]["job_id"]

    header = st.container(key='match-header')
    body = st.container(key='match-body')
    _, left, middle, _ = body.columns([1,2,4,1])
    footer = st.container(key='footer')

    with header:
        header.markdown(com.backgroundImage('st-key-match-header', 'match.png'), unsafe_allow_html=True)
        header.title("Your Match Is Ready!")
        header.text('See below for results')

    with left:
        left_result = left.container(key="match_result")
        total_pane, retry_pane = left_result.columns([1,1])
        total_pane.text(f"{len(matches):,} Jobs are found.")
        if(retry_pane.button("Re-Run and Adjust Filters")):
            st.switch_page("app.py")
        left_pane = left.container(key="left-pane", height=563, border=True, )
        for job in matches:
            isSelected = job["job_id"] == job_id
            left_pane.markdown(com.getJob(job, isSelected), unsafe_allow_html=True)

    with middle:
        middle_container = middle.container(height=620, border=True, key="match-middle-container")
        if matches:
            job = com.find_record_by_jobid(matches, job_id)

            if job:
                score = job["match_scores"]
                details = job["details"]
                mandatory = job["mandatory"]
                preferred = job["preferred"]
                middle_container.subheader(f"{', '.join(details['job_title_base'])} at {', '.join(details['company_name'])}")
                if score["overall_score"]:
                    middle_container.markdown(f'<div class="overall_score_header">✅ Overall = {score["overall_score"]*100:.0f}%</div>', unsafe_allow_html=True)
                if score["overall_skills"]:
                    middle_container.markdown(f'<li class="score_item">🤹🏽 Skill Score: {score["overall_skills"]*100:.0f}%</li>', unsafe_allow_html=True)
                if score["overall_background"]:
                    middle_container.markdown(f'<li class="score_item">🧮 Background Score: {score["overall_background"]*100:.0f}%</li>', unsafe_allow_html=True)
                if score["overall_education"]:
                    middle_container.markdown(f'<li class="score_item">📒 Education Score: {score["overall_education"]*100:.0f}%</li>', unsafe_allow_html=True)
                if score["overall_credentials"]:
                    middle_container.markdown(f'<li class="score_item">📑 Credentials Score: {score["overall_credentials"]*100:.0f}%</li>', unsafe_allow_html=True)

                match_left, match_middle, match_right = middle_container.columns([1,1,1])
                with match_left:
                    if score["overall_mandatory"]:
                        match_left.markdown(f'<div class="score_header">Mandatory = {score["overall_mandatory"]*100:.0f}%</div>', unsafe_allow_html=True)
                    if score["mandatory_skill_score"]:
                        match_left.markdown(f'<li class="score_item">🤹🏽 Skill Score: {score["mandatory_skill_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_background_score"]:
                        match_left.markdown(f'<li class="score_item">🧮 Background Score: {score["mandatory_background_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_education_score"]:
                        match_left.markdown(f'<li class="score_item">📒 Education Score: {score["mandatory_education_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_industry_score"]:
                        match_left.markdown(f'<li class="score_item">Indurstry Score: {score["mandatory_industry_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["mandatory_credentials_score"]:
                        match_left.markdown(f'<li class="score_item">📑 Credentials Score: {score["mandatory_credentials_score"]*100:.0f}%</li>', unsafe_allow_html=True)

                with match_middle:
                    if score["overall_preferred"]:
                        match_middle.markdown(f'<div class="score_header">Preferred = {score["overall_preferred"]*100:.0f}%</div>', unsafe_allow_html=True)
                    if score["preferred_skill_score"]:
                        match_middle.markdown(f'<li class="score_item">🤹🏽 Skill Score: {score["preferred_skill_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_background_score"]:
                        match_middle.markdown(f'<li class="score_item">🧮 Background Score: {score["preferred_background_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_education_score"]:
                        match_middle.markdown(f'<li class="score_item">📒 Education Score: {score["preferred_education_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_industry_score"]:
                        match_middle.markdown(f'<li class="score_item">Indurstry Score: {score["preferred_industry_score"]*100:.0f}%</li>', unsafe_allow_html=True)
                    if score["preferred_credentials_score"]:
                        match_middle.markdown(f'<li class="score_item">📑 Credentials Score: {score["preferred_credentials_score"]*100:.0f}%</li>', unsafe_allow_html=True)

                with match_right:
                    if score["responsibilities_score"]:
                        match_right.markdown(f'<div class="score_header">Responsibilites = {score["responsibilities_score"]*100:.0f}%</div>', unsafe_allow_html=True)

                middle_container.markdown(f'<div id="job-location"><span id="location-label">Location:</span> {"<br>".join(item["city"] + ", " + item["state"] for item in details["location"])}</div>', unsafe_allow_html=True)

                if mandatory:
                    middle_container.subheader("👍🏼 Mandatory Qualificatoins")
                    man_hard_skills = mandatory["hard_skills"]
                    if man_hard_skills:
                        middle_container.markdown(f'<div class="skill-title">Hard Skills:', unsafe_allow_html=True)
                        for hard_skill in man_hard_skills:
                            max_year = max(hard_skill["minyears"])
                            min_year = min(hard_skill["minyears"])
                            if max_year > 0:
                                if min_year > 0 and max_year != min_year:
                                    exp_year = f"{min_year}-{max_year}"
                                else:
                                    exp_year = f"{max_year}+"
                                middle_container.markdown(f'<li class="skill-item">{exp_year} years of {", ".join([item for sublist in hard_skill["skill"] for item in sublist])}</li>', unsafe_allow_html=True)
                            else:
                                middle_container.markdown(f'<li class="skill-item">{", ".join([item for sublist in hard_skill["skill"] for item in sublist])}</li>', unsafe_allow_html=True)
                    man_education =  mandatory["education"]
                    if man_education:
                        middle_container.markdown(f'<div class="skill-item"><span class="skill-title">Education:</span> {", ".join([item for sublist in man_education for item in sublist])}</div>', unsafe_allow_html=True)

                if preferred:
                    middle_container.subheader("👏🏼 Preferred Qualificatoins")
                    man_hard_skills = preferred["hard_skills"]
                    if man_hard_skills:
                        middle_container.markdown(f'<div class="skill-title">Hard Skills:', unsafe_allow_html=True)
                        for hard_skill in man_hard_skills:
                            max_year = max(hard_skill["minyears"])
                            min_year = min(hard_skill["minyears"])
                            if max_year > 0:
                                if min_year > 0 and max_year != min_year:
                                    exp_year = f"{min_year}-{max_year}"
                                else:
                                    exp_year = f"{max_year}+"
                                middle_container.markdown(f'<li class="skill-item">{exp_year} years of {", ".join([item for sublist in hard_skill["skill"] for item in sublist])}</li>', unsafe_allow_html=True)
                            else:
                                middle_container.markdown(f'<li class="skill-item">{", ".join([item for sublist in hard_skill["skill"] for item in sublist])}</li>', unsafe_allow_html=True)
                    man_education =  preferred["education"]
                    if man_education:
                        middle_container.markdown(f'<div class="skill-item"><span class="skill-title">Education:</span> {", ".join([item for sublist in man_education for item in sublist])}</div>', unsafe_allow_html=True)

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()