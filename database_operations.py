import streamlit as st
import mysql.connector
from mysql.connector import Error

@st.cache_resource
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


def update_candidate_details(connection, candidate_id, updated_details):
    try:
        cursor = connection.cursor()
        cursor.execute("USE ResumeDatabase;")

        update_query = """
        UPDATE Candidates 
        SET 
            email = %s, 
            phone_number = %s, 
            location = %s,
            current_role = %s,
            notes = %s
        WHERE candidate_id = %s
        """
        cursor.execute(update_query, (
            updated_details['email'],
            updated_details['phone'],
            updated_details['location'],
            updated_details['current_role'],
            updated_details['notes'],
            candidate_id
        ))
        connection.commit()
        return True
    except Error as e:
        st.error(f"Error updating candidate: {e}")
        return False

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