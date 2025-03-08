import streamlit as st
import utils.common as com

# Streamlit app
def main():
    st.set_page_config(page_title="MIRRA Matcher - Meet the team", layout="wide")
    com.includeCss(st, 'mirra.css')

    team_container = st.container(key='team_container')
    header = team_container.container(key='team-header')
    left1, right1 = team_container.columns([1,1])
    left2, right2 = team_container.columns([1,1])
    left3, right3 = team_container.columns([1,1])
    left4, right4 = team_container.columns([1,1])
    left5, right5 = team_container.columns([1,1])
    bottom = team_container.container(key="team-bottom")

    with header:
        header.markdown(com.backgroundImage('st-key-team-header', 'team.png'), unsafe_allow_html=True)
        header.title("MEET THE TEAM")

    with left1:
        left1_container = left1.container(key='left1-container')
        left1_container.image('./images/cat1.png')

    with right1:
        right1_container = right1.container(key='right1-container')
        right1_container.text('Bio:\nuhiurehgidurhgdiurhfuidrhfiushfuisehfusihfusihdfusihfisuhfsuidfhsiudfhsdiuhfsdiufhsidufhsdiufhsudifhsiudfhsiudfhsiufhsiudhfsudifhsidufhsiudfhsiudfhisduhfisduhfsdiufhsiudfhisudfhsiudfhsduifh')

    with left2:
        left2_container = left2.container(key='left2-container')
        left2_container.text('Bio:\nuhiurehgidurhgdiurhfuidrhfiushfuisehfusihfusihdfusihfisuhfsuidfhsiudfhsdiuhfsdiufhsidufhsdiufhsudifhsiudfhsiudfhsiufhsiudhfsudifhsidufhsiudfhsiudfhisduhfisduhfsdiufhsiudfhisudfhsiudfhsduifh')

    with right2:
        right2_container = right2.container(key='right2-container')
        right2_container.image('./images/cat2.png')

    with left3:
        left3_container = left3.container(key='left3-container')
        left3_container.image('./images/cat1.png')

    with right3:
        right3_container = right3.container(key='right3-container')
        right3_container.text('Bio:\nuhiurehgidurhgdiurhfuidrhfiushfuisehfusihfusihdfusihfisuhfsuidfhsiudfhsdiuhfsdiufhsidufhsdiufhsudifhsiudfhsiudfhsiufhsiudhfsudifhsidufhsiudfhsiudfhisduhfisduhfsdiufhsiudfhisudfhsiudfhsduifh')

    with left4:
        left4_container = left4.container(key='left4-container')
        left4_container.text('Bio:\nuhiurehgidurhgdiurhfuidrhfiushfuisehfusihfusihdfusihfisuhfsuidfhsiudfhsdiuhfsdiufhsidufhsdiufhsudifhsiudfhsiudfhsiufhsiudhfsudifhsidufhsiudfhsiudfhisduhfisduhfsdiufhsiudfhisudfhsiudfhsduifh')

    with right4:
        right4_container = right4.container(key='right4-container')
        right4_container.image('./images/cat2.png')

    with left5:
        left5_container = left5.container(key='left5-container')
        left5_container.image('./images/cat1.png')

    with right5:
        right5_container = right5.container(key='right5-container')
        right5_container.text('Bio:\nuhiurehgidurhgdiurhfuidrhfiushfuisehfusihfusihdfusihfisuhfsuidfhsiudfhsdiuhfsdiufhsidufhsdiufhsudifhsiudfhsiudfhsiufhsiudhfsudifhsidufhsiudfhsiudfhisduhfisduhfsdiufhsiudfhisudfhsiudfhsduifh')

    with bottom:
        bottom_container = bottom.container(key='bottom-container')
        bottom_container.link_button("Start Match", "/" )
        bottom_container.text('MIRRA')

if __name__ == "__main__":
    main()