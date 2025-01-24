import streamlit as st
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import os


# Initialize the embedding model
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# Pinecone setup
PINECONE_API_KEY = "your-pinecone-api-key"  # Replace with your API key
PINECONE_ENVIRONMENT = "your-environment"  # Replace with your environment
INDEX_NAME = "resume-matching"
os.environ['PINECONE_API_KEY'] = "pcsk_6LpRrv_SAE5Taobgp5ATyTsGoberaoCx6pQ9a3ecwY7dViqUvQgRcTgnEazhexmpeEfBzm"
INDEX_NAME = "nea2"
# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(name=INDEX_NAME, dimension=768, metric="cosine")

# Connect to the index
index = pc.Index(INDEX_NAME)

# Helper functions
def chunk_text(text, max_tokens=512):
    """Split text into chunks that fit within the token limit."""
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk.split()) + len(sentence.split()) <= max_tokens:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def embed_resume(resume_text):
    """Chunk and embed a resume."""
    chunks = chunk_text(resume_text)
    embeddings = model.encode(chunks, convert_to_tensor=False)
    return chunks, embeddings

def store_resume(file_name, resume_text):
    """Chunk, embed, and store a resume in Pinecone."""
    chunks, embeddings = embed_resume(resume_text)
    vectors = [
        (f"{file_name}_{i}", embeddings[i], {"resume_id": file_name, "content": chunks[i]})
        for i in range(len(chunks))
    ]
    index.upsert(vectors)  # Store vectors in Pinecone

def search_resumes(job_description, top_k=5):
    """Search for resumes similar to a job description."""
    query_embedding = model.encode(job_description, convert_to_tensor=False)
    query_embedding = query_embedding.tolist()  # Convert NumPy array to list

    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    resume_matches = {}
    for match in results["matches"]:
        resume_id = match["metadata"]["resume_id"]
        content = match["metadata"]["content"]
        if resume_id not in resume_matches:
            resume_matches[resume_id] = []
        resume_matches[resume_id].append(content)

    reconstructed_resumes = {rid: " ".join(chunks) for rid, chunks in resume_matches.items()}
    return reconstructed_resumes


def extract_text_from_pdf(file):
    """Extract text from an uploaded PDF file."""
    import PyPDF2
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def display_resume_cards(resumes):
    """Display resumes as cards in Streamlit."""
    for resume_id, content in resumes.items():
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <h4>Resume ID: {resume_id}</h4>
                <p>{content[:500]}...</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Streamlit interface
st.title("AI Resume Matcher")

# CSS to lock the text box to the bottom
st.markdown(
    """
    <style>
    .stTextArea {
        position: fixed;
        bottom: 0;
        width: 100%;
    }
    .main > div {
        margin-bottom: 100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Upload Resumes
uploaded_files = st.file_uploader("Upload Resumes (PDF)", accept_multiple_files=True, type=["pdf"])
if uploaded_files:
    for uploaded_file in uploaded_files:
        resume_text = extract_text_from_pdf(uploaded_file)  # Extract text from PDF
        store_resume(uploaded_file.name, resume_text)  # Store in Pinecone
    st.success("Resumes uploaded and processed!")

# Search Resumes
job_description = st.text_area("Enter Job Description", key="job_description", label_visibility="hidden")
if st.button("Search"):
    if job_description:
        results = search_resumes(job_description)
        st.write("### Matching Resumes")
        display_resume_cards(results)
    else:
        st.warning("Please enter a job description.")
