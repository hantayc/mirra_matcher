import streamlit as st
import pandas as pd

st.set_page_config(page_title="Job Listings & Resume Upload", layout="wide")

# ====== Sample Job Listings Data ======
jobs = pd.DataFrame(
    [
        {
            "Title": "Data Scientist",
            "Company": "Google",
            "Location": "San Francisco",
            "Description": "Develop ML models for Google Search.",
            "Match Score": 95,
            "Apply Link": "https://www.google.com",
        },
        {
            "Title": "ML Engineer",
            "Company": "Meta",
            "Location": "New York",
            "Description": "Build scalable ML pipelines for Meta.",
            "Match Score": 89,
            "Apply Link": "https://www.google.com",
        },
        {
            "Title": "AI Researcher",
            "Company": "OpenAI",
            "Location": "Remote",
            "Description": "Work on cutting-edge AI projects.",
            "Match Score": 85,
            "Apply Link": "https://www.google.com",
        },
        {
            "Title": "Software Engineer",
            "Company": "Amazon",
            "Location": "Seattle",
            "Description": "Develop scalable cloud solutions for AWS.",
            "Match Score": 80,
            "Apply Link": "https://www.google.com",
        },
        {
            "Title": "NLP Engineer",
            "Company": "Microsoft",
            "Location": "Boston",
            "Description": "Improve NLP models for Azure AI.",
            "Match Score": 78,
            "Apply Link": "https://www.google.com",
        },
    ]
)

# ====== Sidebar Filters ======
st.sidebar.title("🔍 Filter Jobs")
location_filter = st.sidebar.selectbox(
    "📍 Select Location", ["All"] + jobs["Location"].unique().tolist()
)
company_filter = st.sidebar.selectbox(
    "🏢 Select Company", ["All"] + jobs["Company"].unique().tolist()
)

# Apply filters
filtered_jobs = jobs
if location_filter != "All":
    filtered_jobs = filtered_jobs[filtered_jobs["Location"] == location_filter]
if company_filter != "All":
    filtered_jobs = filtered_jobs[filtered_jobs["Company"] == company_filter]

# ====== Resume Upload Section ======
st.title("📂 Upload Your Resume to Find Your Best Job Matches")

uploaded_file = st.file_uploader(
    "Upload Your Resume (PDF or DOCX)", type=["pdf", "docx"]
)

if uploaded_file:
    st.success("✅ Resume uploaded successfully!")
    st.write("Here are your best job matches:")

    # Simulate sorting jobs based on match score
    matched_jobs = jobs.sort_values(by="Match Score", ascending=False)
    st.dataframe(matched_jobs[["Title", "Company", "Location", "Match Score"]])

st.write("---")  # Separator

# ====== Job Listings Section ======
st.title("💼 Available Jobs")

for _, job in filtered_jobs.iterrows():
    with st.expander(f"🔹 {job['Title']} at {job['Company']} ({job['Location']})"):
        st.write(job["Description"])
        st.link_button(f"Apply Now at {job['Company']}", job["Apply Link"])
