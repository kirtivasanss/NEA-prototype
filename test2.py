import streamlit as st
import mysql.connector
import numpy as np
import ast
from sentence_transformers import SentenceTransformer
from candidate_display import *
from candidate import Candidate
from database_operations import *

connection = create_connection()
# --- Utility Functions ---
@st.cache_resource
def load_embedding_model():
    """
    Load and cache the SentenceTransformer model.
    You can change the model name if desired.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model


def get_query_embedding(query_text, model):
    """
    Generate the embedding for the given query text.
    """
    return model.encode(query_text)

@st.cache_resource
def load_resume_embeddings():
    """
    Connects to the MySQL database and retrieves all resume embeddings.
    Assumes each embedding is stored as a string representation of a Python list.
    Returns a list of tuples: (candidate_id, embedding_vector)
    """
    # Retrieve MySQL credentials from Streamlit secrets
    db_config = {
        'host': st.secrets["database"]["host"],
        'user': st.secrets["database"]["user"],
        'password': st.secrets["database"]["password"],
        'database': st.secrets["database"]["database"]
    }

    try:
        conn = mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        st.error(f"Error connecting to MySQL: {err}")
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT candidate_id, embedding FROM ResumeEmbeddings")
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")
        conn.close()
        return []


    rows = cursor.fetchall()
    conn.close()

    resume_data = []
    for candidate_id, embedding_str in rows:
        # Convert the stored string back to a list.
        # Adjust this if your embeddings are stored in a different format.
        try:
            embedding = ast.literal_eval(embedding_str)
        except Exception as e:
            st.error(f"Error parsing embedding for candidate {candidate_id}: {e}")
            continue
        resume_data.append((candidate_id, np.array(embedding)))
    return resume_data


def cosine_similarity(vec1, vec2):
    """
    Compute the cosine similarity between two vectors.
    """
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm1 * norm2)


def aggregate_candidate_scores(query_embedding, resume_data):
    """
    For each candidate (who may have multiple resume chunks), compute a score.
    Here we take the maximum similarity of any chunk as the candidate's score.
    Returns a dict mapping candidate_id to score.
    """
    candidate_scores = {}
    for candidate_id, embedding in resume_data:
        sim = cosine_similarity(query_embedding, embedding)
        if candidate_id in candidate_scores:
            candidate_scores[candidate_id] = max(candidate_scores[candidate_id], sim)
        else:
            candidate_scores[candidate_id] = sim
    return candidate_scores


def searchPage():
    # Initialize the session state variable if it doesn't exist
    if "selected_candidate_id" not in st.session_state:
        st.session_state["selected_candidate_id"] = None

    st.title("Semantic Resume Search")

    # Add a back button when viewing candidate details
    if st.session_state["selected_candidate_id"]:
        candidate_id = st.session_state["selected_candidate_id"]
        candidate_details = fetch_candidate_details(connection, candidate_id)
        display_full_candidate_details(candidate_details)

        if st.button("Back to Search"):
            st.session_state["selected_candidate_id"] = None
            st.rerun()

    else:
        # Rest of your search interface code remains the same
        st.write("Enter a search query to find resumes that semantically match your input.")
        query_text = st.text_area("Enter your search query:")
        top_n = st.number_input("Number of top results to display:", min_value=1, step=1, value=5, max_value=10)

        if st.button("Search"):
            if not query_text.strip():
                st.warning("Please enter a non-empty query.")
                return

            model = load_embedding_model()
            query_embedding = get_query_embedding(query_text, model)
            resume_data = load_resume_embeddings()

            if not resume_data:
                st.error("No resume embeddings found in the database or an error occurred.")
                return

            candidate_scores = aggregate_candidate_scores(query_embedding, resume_data)
            filtered_candidates = list(filter(
                lambda x: x[1] >= 0.1,
                candidate_scores.items()
            ))
            sorted_candidates = sorted(filtered_candidates, key=lambda x: x[1], reverse=True)
            top_candidates = sorted_candidates[:top_n]


            st.subheader("Top Matching Candidates (Similarity Score ≥ 0.7):")
            if top_candidates:
                for candidate_id, score in top_candidates:
                    candidate_details = fetch_candidate_details(connection, candidate_id)

                    candidate = Candidate(
                        candidate_id=candidate_details['candidate_id'],
                        name=candidate_details['name'],
                        email=candidate_details['email'],
                        phone=candidate_details['phone_number'],
                        location=candidate_details['location'],
                        education=candidate_details.get('education', 'No education'),
                        experience=candidate_details.get('work_experience', 'No work experience'),
                        skills=candidate_details.get('skills', 'No skills').split('; ') if candidate_details.get(
                            'skills') else [],
                        currentRole='Not specified',
                        company='Not specified'
                    )
                    st.write(candidate)
                    st.write(f"**Similarity Score:** {score:.2f}")
                    display_candidate_info(candidate)

                    if st.button(f"View Details: {candidate.candidate_id}", key=f"view_{candidate['candidate_id']}"):
                        st.session_state["selected_candidate_id"] = candidate.candidate_id
                        st.rerun()
            else:
                st.info("No candidates found with similarity score ≥ 0.7. Try modifying your search query.")