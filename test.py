import streamlit as st
import mysql.connector






# Streamlit UI
st.title("Candidate Feedback Form")

# Retrieve the reviewer's name from session state
if "reviewer_name" not in st.session_state:
    st.session_state.reviewer_name = "Anonymous"

reviewer = st.session_state.reviewer_name
candidate_id = st.number_input("Candidate ID", min_value=1, step=1)
feedback = st.text_area("Enter Feedback")

if st.button("Submit Feedback"):
    if candidate_id and feedback.strip():
        insert_feedback(candidate_id, feedback, reviewer)
    else:
        st.error("Please enter all required fields.")
