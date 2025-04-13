#!/bin/bash

# Usage: streamlit run rag_chatbot_app.py --server.port 8080 (--server.port 8080 is for Cloud9)
source mirra_env/bin/activate
streamlit run app.py --server.fileWatcherType none