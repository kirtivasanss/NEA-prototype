import struct
from sentence_transformers import SentenceTransformer
from database_operations import *

@st.cache_resource
def create_model():
    MODEL_NAME = "all-MiniLM-L6-v2"
    mdl = SentenceTransformer(MODEL_NAME)
    return mdl


model = create_model()


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


def insert_embeddings(candidate_id, resume_text):
    """Store resume embeddings and metadata in MySQL database."""
    chunks, embeddings = embed_resume(resume_text)

    connection = create_connection()
    cursor = connection.cursor()

    # Insert embeddings
    query = """
    INSERT INTO ResumeEmbeddings (candidate_id, embedding) VALUES (%s, %s)
    """
    for embedding in embeddings:
        embedding_str = ",".join(map(str, embedding))  # Convert embedding array to string
        cursor.execute(query, (candidate_id, embedding_str))
