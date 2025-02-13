import streamlit as st
from candidate_display import *
from candidate import Candidate
from database_operations import *
from random import randint

def search_candidates_by_name(connection, name: str):
    """
    Search for candidates by name in the database.
    """
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT * FROM Candidates 
    WHERE LOWER(name) LIKE LOWER(%s)
    """
    search_term = f"%{name}%"
    cursor.execute(query, (search_term,))
    results = cursor.fetchall()
    cursor.close()
    return results


def viewPage():
    if "selected_candidate_id" not in st.session_state:
        st.session_state["selected_candidate_id"] = None

    st.title("Resume Database Management App")

    connection = create_connection()

    if not st.session_state["selected_candidate_id"]:
        # Add search functionality at the top
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input("Search candidates by name:", "")
        with search_col2:
            clear_search = st.button("Clear Search")
            if clear_search:
                search_query = ""

    # Initialize session state for candidate selection
    if st.session_state["selected_candidate_id"]:
        candidate_id = st.session_state.selected_candidate_id
        candidate_details = fetch_candidate_details(connection, candidate_id)
        display_full_candidate_details(candidate_details,connection)



    if connection:
        if st.session_state.selected_candidate_id:
            # Candidate details page
            candidate = fetch_candidate_details(connection, st.session_state.selected_candidate_id)

            if st.button("Back to Candidates"):
                st.session_state.selected_candidate_id = None
                st.rerun()

        else:
            # Candidate list page
            st.subheader("Candidate List")

            # Determine which candidates to display based on search
            if search_query:
                candidates_data = search_candidates_by_name(connection, search_query)
            else:
                candidates_data = fetch_detailed_candidates(connection)

            if candidates_data:
                for candidate_data in candidates_data:
                    candidate = Candidate(
                        name=candidate_data['name'],
                        email=candidate_data['email'],
                        phone=candidate_data['phone_number'],
                        location=candidate_data['location'],
                        education=candidate_data.get('education','no education'),
                        experience=candidate_data.get('work_experience', 'No work experience'),
                        skills=candidate_data.get('skills', 'No skills').split('; ') if candidate_data.get('skills') else [],
                        currentRole='Not specified',
                        company='Not specified'
                    )

                    display_candidate_info(candidate)

                    if st.button(f"View Details: {candidate.name}", key=f"view_{candidate.name}"):
                        st.session_state.selected_candidate_id = candidate_data['candidate_id']
                        st.rerun()


            else:
                if search_query:
                    st.info("No candidates found matching your search.")
                else:
                    st.info("No candidates in the database.")


if __name__ == "__main__":
    viewPage()