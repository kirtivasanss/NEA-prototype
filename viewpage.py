import streamlit as st
from candidate_card import CandidateInfoApp, Candidate
from candidate_display import *
from database_operations import *

st.set_page_config(
    page_title="View Candidates",
)

# Main app
def main():
    if "selected_candidate_id" not in st.session_state:
        st.session_state["selected_candidate_id"] = None

    st.title("Resume Database Management App")

    connection = create_connection()
    candidate_app = CandidateInfoApp()

    # Initialize session state for candidate selection
    if "selected_candidate_id" in st.session_state:
        candidate_id = st.session_state.selected_candidate_id
        candidate_details = fetch_candidate_details(connection, candidate_id)
        display_full_candidate_details(candidate_details)

    if connection:
        if st.session_state.selected_candidate_id:
            # Candidate details page
            candidate = fetch_candidate_details(connection, st.session_state.selected_candidate_id)

            if st.button("Back to Candidates"):
                st.session_state.selected_candidate_id = None

        else:
            # Candidate list page
            st.subheader("Candidate List")
            candidates = fetch_detailed_candidates(connection)
            if candidates:
                for candidate_data in candidates:
                    candidate = Candidate(
                        name=candidate_data['name'],
                        email=candidate_data['email'],
                        phone=candidate_data['phone_number'],
                        location=candidate_data['location'],
                        education=candidate_data.get('education', 'No education details'),
                        experience=candidate_data.get('work_experience', 'No work experience'),
                        skills=candidate_data.get('skills', 'No skills').split('; ') if candidate_data.get(
                            'skills') else [],
                        currentRole='Not specified',
                        company='Not specified'
                    )
                    candidate_app.display_candidate_info(candidate)

                    if st.button(f"View Details: {candidate.name}", key=f"view_{candidate_data['candidate_id']}"):
                        st.session_state.selected_candidate_id = candidate_data['candidate_id']
                        st.rerun()  # Ensures the page updates immediately


if __name__ == "__main__":
    main()
