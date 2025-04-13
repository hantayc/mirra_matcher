import streamlit as st
import streamlit.components.v1 as components
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
    st.session_state["disabled"] = False
    # matches = json.loads('[]')
    # if 'matches' in st.session_state:
    #     matches = st.session_state['matches']
    # else:
    matches = com.read_json_result('match_result.json')

    matches_str = json.dumps(matches)
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
        total_pane.markdown("<div id='result_count'><span id='num_of_result'>0</span> Jobs are found.</div>", unsafe_allow_html=True)
        if(retry_pane.button("Re-Run and Adjust Filters")):
            st.switch_page("app.py")
        left.container(key="left-pane", height=563, border=True, )

    with middle:
        middle.container(height=620, border=True, key="match-middle-container")
        if matches_str:
            js_call = f"""
                window.onload = () => {{
                    const jsonData = {matches_str};
                    handleData(jsonData);
                }};
                """
            
            com.logger(com.include_js_file('match.js', js_call))
            components.html(com.include_js_file('match.js', js_call), height=0)
            # st.session_state['matches'] = matches

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()