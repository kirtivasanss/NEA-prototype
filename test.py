import streamlit as st
import mysql.connector
from mysql.connector import Error
from candidate_card import CandidateInfoApp, Candidate


# Database connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Emug123$"
        )
        if connection.is_connected():
            print("Connected to MySQL server")
            return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None


# Fetch all candidate summaries
def fetch_detailed_candidates(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("USE ResumeDatabase;")

    query = """
    SELECT 
        c.candidate_id, c.name, c.email, c.phone_number, c.location,
        GROUP_CONCAT(DISTINCT 
            CONCAT(e.degree, ' from ', e.institution, ' (', e.graduation_year, ')') 
            SEPARATOR '; ') AS education,
        GROUP_CONCAT(DISTINCT 
            CONCAT(w.position, ' at ', w.company, ' (', w.years_experience, ' years)') 
            SEPARATOR '; ') AS work_experience,
        GROUP_CONCAT(DISTINCT 
            CONCAT(s.skill_name, ' (', s.skill_level, ')') 
            SEPARATOR '; ') AS skills
    FROM 
        Candidates c
    LEFT JOIN 
        Education e ON c.candidate_id = e.candidate_id
    LEFT JOIN 
        WorkExperience w ON c.candidate_id = w.candidate_id
    LEFT JOIN 
        Skills s ON c.candidate_id = s.candidate_id
    GROUP BY 
        c.candidate_id
    """
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    return records


# Fetch a single candidate's full details
def fetch_candidate_details(connection, candidate_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("USE ResumeDatabase;")

    query = """
    SELECT 
        c.candidate_id, c.name, c.email, c.phone_number, c.location,
        GROUP_CONCAT(DISTINCT 
            CONCAT(e.degree, ' from ', e.institution, ' (', e.graduation_year, ')') 
            SEPARATOR '; ') AS education,
        GROUP_CONCAT(DISTINCT 
            CONCAT(w.position, ' at ', w.company, ' (', w.years_experience, ' years)') 
            SEPARATOR '; ') AS work_experience,
        GROUP_CONCAT(DISTINCT 
            CONCAT(s.skill_name, ' (', s.skill_level, ')') 
            SEPARATOR '; ') AS skills
    FROM 
        Candidates c
    LEFT JOIN 
        Education e ON c.candidate_id = e.candidate_id
    LEFT JOIN 
        WorkExperience w ON c.candidate_id = w.candidate_id
    LEFT JOIN 
        Skills s ON c.candidate_id = s.candidate_id
    WHERE 
        c.candidate_id = %s
    GROUP BY 
        c.candidate_id
    """
    cursor.execute(query, (candidate_id,))
    record = cursor.fetchone()
    cursor.close()
    return record

def display_full_candidate_details(candidate):
    """
    Display the full details of a candidate on a separate page with styled tags for skills.
    """
    st.title(f"Details for {candidate['name']}")

    # Candidate details
    st.write(f"📧 **Email:** {candidate['email']}")
    st.write(f"📞 **Phone:** {candidate['phone_number']}")
    st.write(f"📍 **Location:** {candidate['location']}")

    st.markdown("---")

    # Education
    st.subheader("🎓 Education")
    st.write(candidate.get("education", "No education details available."))

    st.markdown("---")

    # Work Experience
    st.subheader("💼 Work Experience")
    st.write(candidate.get("work_experience", "No work experience available."))

    st.markdown("---")

    # Skills as tags
    st.subheader("🛠️ Skills")
    skills = candidate.get("skills", [])
    if skills:
        # Use HTML for styled skill tags
        skills_html = "".join([
            f"""<span style="
            display: inline-block; 
            background-color: #FF4B4B; 
            color: white; 
            padding: 5px 10px; 
            margin: 5px 5px 0 0; 
            border-radius: 15px; 
            font-size: 14px;">{skill}</span>"""
            for skill in skills
        ])
        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.write("No skills available.")


# Main app
def main():
    if "selected_candidate_id" not in st.session_state:
        st.session_state["selected_candidate_id"] = None

    st.title("Resume Database Management")

    connection = create_connection()
    candidate_app = CandidateInfoApp()

    # Initialize session state for candidate selection
    if "selected_candidate_id" in st.session_state:
        candidate_id = st.session_state.selected_candidate_id
        candidate_details = fetch_candidate_details(connection, candidate_id)

        if candidate_details:
            # Format skills as a list
            candidate_details["skills"] = (
                candidate_details["skills"].split("; ") if candidate_details.get("skills") else []
            )
            display_full_candidate_details(candidate_details)

    if connection:
        if st.session_state.selected_candidate_id:
            # Candidate details page

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
