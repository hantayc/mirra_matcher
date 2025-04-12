import streamlit as st
import utils.common as com

# Streamlit app
def main():
    st.set_page_config(page_title="MIRRA Matcher - Why Mirra?", layout="wide")
    st.markdown(com.loadFont(), unsafe_allow_html=True)
    com.includeCss(st, 'why.css')
    st.markdown('<span class="gradient-overlay"></span>', unsafe_allow_html=True)
    st.session_state["disabled"] = False

    header = st.container(key='why-header')
    _, middle, _ = st.columns([3,4,3])
    left, right = st.columns([1,1])
    _, bottom_middle, _ = st.columns([3,4,3])
    footer = st.container(key='footer')

    with header:
        header.markdown(com.backgroundImage('st-key-why-header', 'why.png'), unsafe_allow_html=True)
        title_container = header.container(key='title-container')
        title_container.title("Why MIRRA?")
        title_container.text('Everything You Need To Know')

    with middle:
        middle_container = middle.container(key="middle-container")
        middle_container.title("Information to know about MIRRA")
        middle_container.text("MIRRA stands for Matching Intelligence for Resume & Role Alignment. It’s an AI-powered platform that analyzes your resume, identifies key qualifications, and compares them against job postings to find the best matches. By focusing on semantic similarity—rather than just keywords—MIRRA provides transparent insights into which roles truly align with your skills and career goals. This saves time, helps you discover new opportunities, and streamlines the entire job search process.")
        middle_container.subheader("Would you consider using MIRRA?")
        middle_container.text("MIRRA is an AI-driven platform designed to align your resume with the most suitable job opportunities. By analyzing your unique skills, experiences, and career goals, MIRRA pinpoints roles that genuinely match your profile—saving you time and effort in the application process. Its transparent approach also highlights how well you meet each requirement, helping you focus on positions where you’ll thrive.")
        middle_container.subheader("Experience a New Way to Job Hunt")
        middle_container.text("No more guesswork, no more sifting through irrelevant listings. MIRRA goes beyond standard job boards to show you exactly how your skills align with each role’s requirements. By highlighting the clearest paths to success, MIRRA helps you focus on opportunities that truly matter, saving you time and boosting your confidence in every application.")

    with left:
        left_container = left.container(key="left-container")
        left_container.markdown(com.backgroundImage('st-key-left-container', 'search.png'), unsafe_allow_html=True)

    with right:
        right_container = right.container(key='right-container')
        right_container.title(f"Nearly 40% of applicants realize halfway through a job description that they lack a key requirement—wasting valuable time on roles that aren’t a good fit")
    
    with bottom_middle:
        bottom_container = bottom_middle.container(key='bottom-container')
        bottom_container.title('This tool can land you your next role.')

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()