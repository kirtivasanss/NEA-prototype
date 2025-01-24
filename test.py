import streamlit as st
import mysql.connector

# Function to fetch candidates from the database based on search criteria
def search_candidates(search_query, connection):
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to fetch rows as dictionaries
    query = """
    SELECT candidate_id, name, email, phone_number, location, graduation_year 
    FROM Candidates
    WHERE name LIKE %s OR email LIKE %s OR location LIKE %s
    """
    search_term = f"%{search_query}%"  # For partial matching
    cursor.execute(query, (search_term, search_term, search_term))
    candidates = cursor.fetchall()
    cursor.close()
    return candidates

# Function to display candidates as cards
def display_candidates(connection):
    st.title("Search Resumes")
    search_query = st.text_input("Search by Name, Email, or Location", "")

    # Fetch candidates based on the search query
    if search_query:
        candidates = search_candidates(search_query, connection)

        if candidates:
            st.subheader(f"Found {len(candidates)} Candidate(s)")
            for candidate in candidates:
                # Display each candidate in a card
                with st.container():
                    st.markdown(
                        f"""
                        **Name:** {candidate['name']}  
                        **Email:** {candidate['email']}  
                        **Phone Number:** {candidate['phone_number']}  
                        **Location:** {candidate['location']}  
                        **Graduation Year:** {candidate['graduation_year']}  
                        """,
                        unsafe_allow_html=True,
                    )

                    # View details button for each candidate
                    if st.button(
                        f"View Details: {candidate['name']}",
                        key=f"view_{candidate['candidate_id']}",
                    ):
                        st.session_state.selected_candidate_id = candidate["candidate_id"]
                        st.experimental_rerun()  # Refresh the page to show details for the selected candidate
        else:
            st.info("No candidates found. Try refining your search.")
    else:
        st.info("Enter a search query to find candidates.")

# Main function
def main():
    # Establish database connection
    connection = mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database",
    )

    # Ensure connection is closed properly
    try:
        display_candidates(connection)
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
