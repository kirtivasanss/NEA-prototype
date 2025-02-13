import streamlit as st
from candidate import Candidate
import time
from database_operations import *

connection = create_connection()
cursor = connection.cursor()
def display_candidate_info(candidate):
    """
    Display a styled, clickable card for the candidate with their information.
    """
    # Define a unique key for each card using candidate_id
    unique_key = f"card_{candidate.candidate_id or candidate.name.replace(' ', '_')}"

    # Make the card clickable using an invisible link styled as a card
    card_html = f"""
    <a href="?selected_candidate_id={candidate.candidate_id}" style="text-decoration: none; color: inherit;">
        <div style=" 
            border-radius: 10px; 
            padding: 15px; 
            margin-bottom: 50px; 
            background-color: #262730;
            box-shadow: 0 8px 20px #393A48;
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
            <h3 style="margin: 5px; color:  ;">{candidate.name}</h3>
            <p style="margin: 5px 0 0; color: #FAFAFA;">📧 {candidate.email}</p>
            <p style="margin: 5px 0 0; color: #FAFAFA;">📞 {candidate.phone}</p>
            <p style="margin: 5px 0 0; color: #FAFAFA;">📍 {candidate.location}</p>
        </div>
    </a>
    """
    # Render the card
    st.markdown(card_html, unsafe_allow_html=True)


def display_full_candidate_details(candidate, db_connection):
    """
    Display the full details of a candidate on a separate page with styled tags for skills.
    """
    if candidate:
        # Format skills, education, and work experience as lists
        candidate["skills"] = (
            candidate["skills"].split("; ") if candidate.get("skills") else []
        )
        candidate["education"] = (
            candidate["education"].split("; ") if candidate.get("education") else []
        )
        candidate["work_experience"] = (
            candidate["work_experience"].split("; ") if candidate.get("work_experience") else []
        )

        st.title(f"{candidate['name']}")
        display_info(candidate)

        st.markdown("---")

        # Education Section
        st.subheader("🎓 Education")
        education = candidate.get("education", [])
        if education:
            for edu in education:
                degree, institution, year = parse_education_entry(edu)
                display_education(
                    institution,
                    degree,
                    graduation_year=f"Graduation Year: {year}",
                )
        else:
            st.write("No education details available.")

        # Work Experience Section
        st.subheader("💼 Work Experience")
        experience = candidate.get("work_experience", [])
        if experience:
            for exp in experience:
                position, company, years, description = parse_experience_entry(exp)
                display_experience(
                    position=position,
                    company=company,
                    years=f"Experience: {years}",
                    description=description,
                )
        else:
            st.write("No work experience available.")

        # Skills Section
        st.subheader("🛠️ Skills")
        skills = candidate.get("skills", [])
        if skills:
            display_skills(skills)
        else:
            st.write("No skills available.")

        st.markdown("---")

        # Display Feedback Section
        st.subheader("📢 Candidate Feedback")
        candidate_id = candidate.get("candidate_id")
        if candidate_id:
            cursor = db_connection.cursor()
            cursor.execute("SELECT feedback, reviewer FROM CandidateFeedback WHERE candidate_id = %s", (candidate_id,))
            feedback_records = cursor.fetchall()
            cursor.close()

            if feedback_records:
                for feedback_entry in feedback_records:
                    st.markdown(f"**{feedback_entry[1]}**: {feedback_entry[0]}")
                    st.markdown("---")
            else:
                st.write("No feedback available for this candidate.")
        else:
            st.write("Candidate ID not found. Cannot fetch feedback.")

        # Feedback Section
        st.subheader("📝 Provide Feedback")
        feedback = st.text_area("Enter your feedback:")
        reviewer = st.text_input("Your Name:")

        if st.button("Submit Feedback"):
            if feedback and reviewer:
                candidate_id = candidate.get("candidate_id")
                if candidate_id:
                    try:
                        cursor = db_connection.cursor()
                        insert_feedback(cursor, candidate_id, feedback, reviewer)
                        db_connection.commit()
                        cursor.close()
                        st.success("Feedback submitted successfully!")
                    except Exception as e:
                        st.error(f"Error submitting feedback: {e}")
                else:
                    st.error("Candidate ID not found. Cannot submit feedback.")
            else:
                st.error("Please enter both feedback and your name.")

        # Delete Candidate Button
        if st.button("Delete Candidate"):
            candidate_id = candidate.get("candidate_id")
            if candidate_id:
                try:
                    delete_candidate(candidate_id)  # Ensure delete_candidate() is defined
                    st.success("Candidate successfully deleted.")
                except Exception as e:
                    st.error(f"Error deleting candidate: {e}")
            else:
                st.error("Candidate ID not found. Cannot delete candidate.")

        # Edit Candidate Details Button
        if st.button("Edit Candidate Details"):
            display_update_inputs(candidate)




def display_update_inputs(candidate=None):
    st.title("Update Data in All Tables")

    # Create tabs for each table
    tab_candidates, tab_education, tab_work, tab_skills, tab_embeddings, tab_feedback = st.tabs(
        ["Candidates", "Education", "Work Experience", "Skills", "Resume Embeddings", "Candidate Feedback"]
    )

    # ----- Candidates Tab -----
    with tab_candidates:
        st.header("Candidates Table")
        with st.form("form_update_candidate"):
            candidate_id_default = str(candidate.get("candidate_id")) if candidate and candidate.get(
                "candidate_id") else ""
            name_default = candidate.get("name", "") if candidate else ""
            email_default = candidate.get("email", "") if candidate else ""
            phone_default = candidate.get("phone_number", "") if candidate else ""
            location_default = candidate.get("location", "") if candidate else ""

            candidate_id = st.text_input("Candidate ID", value=candidate_id_default)
            name = st.text_input("Name", value=name_default)
            email = st.text_input("Email", value=email_default)
            phone_number = st.text_input("Phone Number", value=phone_default)
            location = st.text_input("Location", value=location_default)

            submitted = st.form_submit_button("Update Candidate")
            if submitted:
                if candidate_id and name and email:
                    update_candidate(candidate_id, name, email, phone_number, location)
                else:
                    st.error("Candidate ID, Name, and Email are required.")

    # ----- Education Tab -----
    with tab_education:
        st.header("Education Table")
        with st.form("form_update_education"):
            education_id = st.text_input("Education ID")
            candidate_id_default = str(candidate.get("candidate_id")) if candidate and candidate.get(
                "candidate_id") else ""
            candidate_id = st.text_input("Candidate ID", value=candidate_id_default)
            degree = st.text_input("Degree")
            institution = st.text_input("Institution")
            graduation_year = st.number_input("Graduation Year", min_value=1900, max_value=2100, step=1)

            submitted = st.form_submit_button("Update Education")
            if submitted:
                if education_id and candidate_id:
                    update_education(education_id, candidate_id, degree, institution, graduation_year)
                else:
                    st.error("Education ID and Candidate ID are required.")

    # ----- Work Experience Tab -----
    with tab_work:
        st.header("Work Experience Table")
        with st.form("form_update_work"):
            work_id = st.text_input("Work Experience ID")
            candidate_id_default = str(candidate.get("candidate_id")) if candidate and candidate.get(
                "candidate_id") else ""
            candidate_id = st.text_input("Candidate ID", value=candidate_id_default, key="update_work_candidate_id")
            position = st.text_input("Position")
            company = st.text_input("Company")
            years_experience = st.number_input("Years of Experience", min_value=0, max_value=100, step=1)
            description = st.text_area("Description")

            submitted = st.form_submit_button("Update Work Experience")
            if submitted:
                if work_id and candidate_id:
                    update_work_experience(work_id, candidate_id, position, company, years_experience, description)
                else:
                    st.error("Work Experience ID and Candidate ID are required.")

    # ----- Skills Tab -----
    with tab_skills:
        st.header("Skills Table")
        with st.form("form_update_skills"):
            skill_id = st.text_input("Skill ID")
            candidate_id_default = str(candidate.get("candidate_id")) if candidate and candidate.get(
                "candidate_id") else ""
            candidate_id = st.text_input("Candidate ID", value=candidate_id_default, key="update_skills_candidate_id")
            skill_name = st.text_input("Skill Name")

            submitted = st.form_submit_button("Update Skill")
            if submitted:
                if skill_id and candidate_id:
                    update_skill(skill_id, candidate_id, skill_name)
                else:
                    st.error("Skill ID and Candidate ID are required.")

    # ----- Resume Embeddings Tab -----
    with tab_embeddings:
        st.header("Resume Embeddings Table")
        with st.form("form_update_embeddings"):
            embedding_id = st.text_input("Embedding ID")
            candidate_id_default = str(candidate.get("candidate_id")) if candidate and candidate.get(
                "candidate_id") else ""
            candidate_id = st.text_input("Candidate ID", value=candidate_id_default,
                                         key="update_embedding_candidate_id")
            embedding = st.text_area("Embedding")

            submitted = st.form_submit_button("Update Resume Embedding")
            if submitted:
                if embedding_id and candidate_id:
                    update_resume_embedding(embedding_id, candidate_id, embedding)
                else:
                    st.error("Embedding ID and Candidate ID are required.")

    # ----- Candidate Feedback Tab -----
    with tab_feedback:
        st.header("Candidate Feedback Table")
        with st.form("form_update_feedback"):
            feedback_id = st.text_input("Feedback ID")
            candidate_id_default = str(candidate.get("candidate_id")) if candidate and candidate.get(
                "candidate_id") else ""
            candidate_id = st.text_input("Candidate ID", value=candidate_id_default, key="update_feedback_candidate_id")
            feedback = st.text_area("Feedback")
            reviewer = st.text_input("Reviewer")

            submitted = st.form_submit_button("Update Candidate Feedback")
            if submitted:
                if feedback_id and candidate_id:
                    update_candidate_feedback(feedback_id, candidate_id, feedback, reviewer)
                else:
                    st.error("Feedback ID and Candidate ID are required.")



def display_education(instution_name, degree, graduation_year):
    """
    Display a card-like component for better readability.
    """
    st.markdown(f"""
    <div style="
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 20px; 
        background-color: #262730;
        box-shadow: 0px 5px 5px #393A48;
    ">
        <h4 style="margin: 0; color: #FAFAFA;">{instution_name}</h4>
        <p style="margin: 5px 0 0; color: #f0f3f4;"><b>{degree}</b></p>
        <p style="margin: 5px 0 0; color: #b3b6b7;"><b>{graduation_year}</b></p>  
    </div>
    """, unsafe_allow_html=True)

def display_experience(company, position, years,description):
    """
    Display a card-like component for better readability.
    """
    st.markdown(f"""
    <div style="
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 20px; 
        background-color: #262730;
        box-shadow: 0px 5px 5px #393A48;
    ">
        <h4 style="margin: 0; color: #FAFAFA;">{company}</h4>
        <p style="margin: 5px 0 0; color: #f0f3f4;"><b>{position}</b></p>
        <p style="margin: 5px 0 0; color: #b3b6b7;"><b>{years}</b></p>  
        <p style="margin: 5px 0 0; color: #b3b6b7;"><b>{description}</b></p>  
    </div>
    """, unsafe_allow_html=True)
def display_skills(skills):
    """
    Display a card-like component for better readability.
    """
    skills_html = "".join([
        f"""<span style="
                    border-radius: 10px; 
                    padding: 9px; 
                    margin: 10px 5px 0 0; 
                    background-color: #262730;
                    box-shadow: 0 3px 9px #e74c3c; 
                    display: inline-block; 
                    background-color: #FF4B4B; 
                    color: white; 
                    border-radius: 12px; 
                    font-size: 12px;"><b>{skill}</b></span>"""
        for skill in skills
    ])
    st.markdown(skills_html, unsafe_allow_html=True)

def display_info(candidate):
    """
    Display a card-like component for better readability.
    """
    if candidate:
        st.markdown(f"""
        <div style="
            border-radius: 10px; 
            padding: 15px; 
            margin-bottom: 20px; 
            background-color: #262730;
            box-shadow: 0px 5px 5px #393A48;
        ">
            <h4 style="margin: 0; color: #FAFAFA;">Email: {candidate['email']}</h4>  
            <h4 style="margin: 0; color: #FAFAFA;">Phone:{candidate['phone_number']}</h4>
            <h4 style="margin: 0; color: #FAFAFA;">Location: {candidate['location']}</h4>
        </div>
        """, unsafe_allow_html=True)

def parse_education_entry(edu_entry):
    """
    Parse an education entry into its components.
    Format: 'degree from institution (year)'
    """
    try:
        degree, rest = edu_entry.split(' from ')
        institution, year = rest.split(' (')
        year = year.replace(')', '')
        return degree, institution, year
    except ValueError:
        return edu_entry, "Unknown Institution", "Unknown Year"


def delete_candidate_from_db(candidate_id, conn):
    """
    Delete a candidate and all related records from the database.
    """
    cursor = None
    try:
        cursor = conn.cursor()

        # Print debug information
        st.write(f"Attempting to delete candidate with ID: {candidate_id}")

        # Delete from Candidates table
        delete_query = "DELETE FROM Candidates WHERE candidate_id = %s"
        cursor.execute(delete_query, (candidate_id,))

        # Check if any row was actually deleted
        if cursor.rowcount == 0:
            raise Exception(f"No candidate found with ID {candidate_id}")

        # Commit the changes
        conn.commit()
        st.write(f"Successfully deleted candidate {candidate_id}")
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        st.write(f"Error in delete_candidate_from_db: {str(e)}")
        raise e

    finally:
        if cursor:
            cursor.close()
def parse_experience_entry(exp_entry):
    """
    Parse a work experience entry into its components.
    Format: 'position at company (years)'
    """
    try:
        position, rest = exp_entry.split(' at ')
        rest, description = rest.split(' desc')
        company, years = rest.split(' (')
        years = years.replace(' years)', '')
        return position, company, years, description
    except ValueError:
        return exp_entry, "Unknown Company", "Unknown Duration", "Description"