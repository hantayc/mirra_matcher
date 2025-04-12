import streamlit as st
import utils.common as com

steps = [{
    'title': 'Upload Resume',
    'emoji': '📂',
    'instruction': ['Drag and drop your PDF resume or use the “Browse File” option.','Our system will quickly parse your qualifications.']
},{
    'title': 'Set Filters',
    'emoji': '✅',
    'instruction': ['Specify job type, location, salary range, or any other relevant criteria.','Tailor your search to focus on the opportunities that matter most to you.']
},{
    'title': 'Start Match',
    'emoji': '🚀',
    'instruction': ['Click the “Start Match” button to begin the analysis of your resume.','A pop-up will appear stating “Results Loading… Please Hold Tight⏳" while the system refines your results.']
},{
    'title': 'View Outputs',
    'emoji': '📊',
    'instruction': ['After processing, you’ll see a list of best-fit job matches.','Explore each listing for more detailed insights.']
},{
    'title': 'Re-Run and Adjust Filters',
    'emoji': '🔄',
    'instruction': ['If you’d like to refine your criteria, select “Re-Run and Adjust Filters.”','This returns you to the home page, where you can update filters and generate fresh results.']
}]

# Streamlit app
def main():
    st.set_page_config(page_title="MIRRA Matcher - How it works", layout="wide")
    st.markdown(com.loadFont(), unsafe_allow_html=True)
    com.includeCss(st, 'works.css')
    st.session_state["disabled"] = False
    st.empty()
    header = st.container(key='works-header')
    _, middle, _ = st.columns([3,4,3])

    footer = st.container(key='footer')

    with header:
        header.markdown(com.backgroundImage('st-key-works-header', 'works.png'), unsafe_allow_html=True)
        header.title("How Does it Work?")

    with middle:
        middle_container = middle.container(key="middle-container")
        middle_container.title("The Steps You Need to Know:")
        for index, step in enumerate(steps):
            middle_container.text(f"{index+1}. {step['title']} {step['emoji']}")
            for ins in step['instruction']:
                middle_container.text(f"- {ins}")

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()