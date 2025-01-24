import streamlit as st
import pinecone
import numpy as np
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
import fitz  # PyMuPDF for PDF extraction
from pinecone import Pinecone, ServerlessSpec
import os
from sentence_transformers import SentenceTransformer
# Initialize Pinecone
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', trust_remote_code=True)
# In case you want to reduce the maximum length:
model.max_seq_length = 8192

os.environ['PINECONE_API_KEY'] = "pcsk_6LpRrv_SAE5Taobgp5ATyTsGoberaoCx6pQ9a3ecwY7dViqUvQgRcTgnEazhexmpeEfBzm"
INDEX_NAME = "nea"

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(name=INDEX_NAME, dimension=768, metric="cosine")

# Connect to the index
index = pc.Index(INDEX_NAME)


# Load the model and tokenizer


# Function to extract text from PDF
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    return text


# Function to generate embeddings



# Streamlit session state initialization
if "uploaded_resumes" not in st.session_state:
    st.session_state["uploaded_resumes"] = []  # List to store uploaded resumes
if "query_results" not in st.session_state:
    st.session_state["query_results"] = []  # List to store query results

# Sidebar: Upload Resumes
st.sidebar.header("Upload Resumes")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF Resumes", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Extract text and generate embeddings
        resume_text = extract_text_from_pdf(uploaded_file)
        embedding = model.encode(resume_text)

        # Upsert to Pinecone
        index.upsert(
            vectors=[
                (
                    uploaded_file.name,  # Use the file name as the unique ID
                    embedding,
                    {"content": resume_text},
                )
            ]
        )
        # Store uploaded resumes in session state
        st.session_state["uploaded_resumes"].append(
            {"file_name": uploaded_file.name, "content": resume_text}
        )
    st.sidebar.success("Resumes uploaded and indexed successfully!")

# Main Page: Job Description Search
st.title("Resume Matching with AI")

job_description = st.text_area("Enter Job Description", height=200)

if st.button("Search"):
    if not job_description.strip():
        st.warning("Please enter a job description.")
    else:
        # Generate embedding for job description
        query_embedding = model.encode(job_description,prompt_name="query")

        # Query Pinecone
        results = index.query(
            vector=query_embedding, top_k=5, include_metadata=True
        )

        # Store query results in session state
        st.session_state["query_results"] = results["matches"]

# Display Query Results
if st.session_state["query_results"]:
    st.subheader("Matching Resumes")
    for match in st.session_state["query_results"]:
        st.write(f"**File Name**: {match['id']}")
        st.write(f"**Similarity Score**: {match['score']:.4f}")
        st.write(f"**Content**: {match['metadata']['content'][:300]}...")  # Display the first 300 characters
        st.write("---")
