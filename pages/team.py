import streamlit as st
import utils.common as com

members = [{
    'pic': 'cat2.png',
    'bio': 'uhiurehgidurhgdiurhfuidrhfiushfuisehfusihfusihdfusihfisuhfsuidfhsiudfhsdiuhfsdiufhsidufhsdiufhsudifhsiudfhsiudfhsiufhsiudhfsudifhsidufhsiudfhsiudfhisduhfisduhfsdiufhsiudfhisudfhsiudfhsduifh.'
},{
    'pic': 'tay.jpg',
    'bio': 'Hi all! I’m Tay, and I’ve been leading the implementation of MIRRA’s matching algorithm. My goal is simple: to make the job search process smarter, fairer, and more transparent—for everyone. Whether you’re switching industries, reentering the workforce, or searching for that next big opportunity, MIRRA is here to help illuminate your path. As we continue building this platform—and aim to integrate our intelligence into the systems used by recruiters and hiring leaders—I’m excited to help bridge the gap between potential and opportunity. I’m currently wrapping up my master’s in Information and Data Science at UC Berkeley, and I work as a Data Scientist focused on data governance—ensuring organizations use their data responsibly, consistently, and effectively. Thanks for stopping by. I’m so glad you’re here, and I hope MIRRA helps you get one step closer to your dream role.'
},{
    'pic': 'tess.jpg',
    'bio': 'Tess Cotter is a strategy and research manager at OpenResearch. She previously worked as a strategy consultant at Publicis Sapient and taught product management at iXperience. Tess is currently pursuing an MS in data science from UC Berkeley and graduated with honors from Tufts University with a BS in engineering psychology and economics. While there, she conducted research in the Spatial Cognition Lab and helped nonprofits and early-stage startups scale their impact with 180 Degrees Consulting.'
},{
    'pic': 'carrie.jpg',
    'bio': 'Carrie led the exploratory data analysis (EDA) and worked on the user interface design for MIRRA, drawing on her strong background in finance consulting to bring a results-driven perspective to the team. She currently works in finance consulting, where she specializes in delivering data-driven solutions that streamline processes and uncover actionable insights.'
},{
    'pic': 'yong.jpg',
    'bio': 'Yong is a Principal Software Developer and Technical Delivery Manager at Zenith Insurance Company, as well as the Application Lead for MIRRA, a capstone project at UC Berkeley. Yong plays a key role in integrating backend and frontend code, overseeing AWS setup and monitoring, and managing the entire development process. Nearing completion of the MIDS program at UC Berkeley, Yong is excited to apply advanced data science concepts to projects like MIRRA and make impactful contributions to both technology and insurance industries.'
}]

# Streamlit app
def main():
    st.set_page_config(page_title="MIRRA Matcher - Meet the team", layout="wide")
    st.markdown(com.loadFont(), unsafe_allow_html=True)
    com.includeCss(st, 'mirra.css')

    team_container = st.container(key='team_container')
    header = team_container.container(key='team-header')

    with header:
        header.markdown(com.backgroundImage('st-key-team-header', 'team.png'), unsafe_allow_html=True)
        header.title("MEET THE TEAM")

    for index, member in enumerate(members):
        left, right = team_container.columns([1,1])
        if index % 2 == 0:
            pic_container = left.container(key=f'pic-container{index}')
            bio_container = right.container(key=f'bio-container{index}')
        else:
            bio_container = left.container(key=f'bio-container{index}')
            pic_container = right.container(key=f'pic-container{index}')
        pic_container.markdown(com.backgroundImage(f'st-key-pic-container{index}', member['pic']), unsafe_allow_html=True)
        bio_container.text('Bio:\n' + member['bio'])

    
    bottom = team_container.container(key="team-bottom")
    footer = st.container(key='footer')

    with bottom:
        bottom_container = bottom.container(key='bottom-container')
        if(bottom_container.button("Start Match")):
            st.switch_page("app.py")
        bottom_container.text('MIRRA')

    with footer:
        footer.markdown('<div class="footer">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster! <span class="copyright"> © 2025 Mirra Matcher. All rights reserved.</span></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()