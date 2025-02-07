import streamlit as st
import utils.common as com

# Streamlit app
def main():
    st.set_page_config(page_title="Mirra Matcher", layout="wide")
    com.includeCss(st, 'mirra.css')
    com.header(st)

    buff, col, buff2 = st.columns([1,2,1])
    # Page title and description
    com.backgroundImage(buff, 'bg-image-left', 'bg1.png')

    col.markdown("""
        <h2>Welcome to Mirra Matcher</h2>
        <div class="product-description">Experience Smarter Job Searches with Our AI-Powered Precision. Find the Perfect Match Faster!</div>
    """, unsafe_allow_html=True)

    com.backgroundImage(buff2, 'bg-image-right', 'bg2.png')

    # Upload button
    col.markdown("<h5>Upload Resume</h5>", unsafe_allow_html=True)
    pdf_file = col.file_uploader("Choose a resume file in a pdf format", type="pdf", key='pdf_uploader')

    if pdf_file is not None:
        st.markdown("<h3>Uploaded Resume:</h3>", unsafe_allow_html=True)
        st.write(f"Uploaded: {pdf_file.name}")
        
        with st.expander("Show resume content"):
            # Extract text from PDF
            extracted_text = com.extract_text_from_pdf(pdf_file)
            st.markdown("<h2>Extracted Text:</h2>", unsafe_allow_html=True)
            st.write(extracted_text)


        st.markdown("<h3>Job Listings</h3>", unsafe_allow_html=True)
        com.display_job_postings(st)

    com.footer(st)

if __name__ == "__main__":
    main()