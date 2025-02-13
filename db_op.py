
import streamlit as st
import sqlite3
from sqlite3 import Error
from dateutil.relativedelta import relativedelta
import datetime


@st.cache_resource
def create_connection():
    """
    Create and cache a SQLite database connection with foreign key support.
    Handles connection errors and displays them in Streamlit.
    """
    try:
        conn = sqlite3.connect('ResumeDatabase.db')
        # Enable foreign key constraints for SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        print("Connected to SQLite database")
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None
    except Exception as e:
        st.error(f"General error: {e}")
        return None


def fetch_candidate_details(connection, candidate_id):
    """
    Fetch consolidated candidate details with error handling.
    Returns a single candidate record or None if not found.
    """
    if not connection:
        st.error("No database connection")
        return None

    try:
        cursor = connection.cursor()
        query = """
        SELECT 
            c.candidate_id, c.name, c.email, c.phone_number, c.location,
            GROUP_CONCAT(DISTINCT 
                (e.degree || ' from ' || e.institution || ' (' || e.graduation_year || ')') 
                , '; ') AS education,
            GROUP_CONCAT(DISTINCT 
                (w.position || ' at ' || w.company || ' (' || w.years_experience || ' years), desc ' || w.description) 
                , '; ') AS work_experience,
            GROUP_CONCAT(DISTINCT 
                (s.skill_name || ' ') 
                , '; ') AS skills
        FROM Candidates c
        LEFT JOIN Education e ON c.candidate_id = e.candidate_id
        LEFT JOIN WorkExperience w ON c.candidate_id = w.candidate_id
        LEFT JOIN Skills s ON c.candidate_id = s.candidate_id
        WHERE c.candidate_id = ?
        GROUP BY c.candidate_id
        """
        cursor.execute(query, (candidate_id,))
        record = cursor.fetchone()

        # Convert tuple result to dictionary
        if record:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, record))
        return None

    except Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        cursor.close()




def insert_candidate_data(cursor, candidate_data):
    """
    Insert or update candidate data with SQLite UPSERT functionality.
    Returns last inserted row ID or None on error.
    """
    try:
        query = """INSERT INTO Candidates (name, email, phone_number, location) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                name = excluded.name,
                phone_number = excluded.phone_number,
                location = excluded.location"""
        cursor.execute(query, (
            candidate_data['name'],
            candidate_data['email'],
            candidate_data['phone_number'],
            candidate_data['location']
        ))
        return cursor.lastrowid
    except Error as e:
        st.error(f"Error saving candidate: {e}")
        return None


def insert_education_data(cursor, candidate_id, education_data):
    """
    Insert education records with date validation.
    Handles special date cases like 'Current' and 'Present'.
    """
    try:
        query = """INSERT INTO Education 
                (candidate_id, degree, institution, graduation_year) 
                VALUES (?, ?, ?, ?)"""

        for edu in education_data:
            end_date = edu.get('end_date', '')
            try:
                if end_date.lower() in ["current", "present", "not available"]:
                    year = datetime.datetime.now().year
                else:
                    dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                    year = dt.year
            except (ValueError, TypeError) as e:
                year = 0  # Default to 0 for invalid dates

            cursor.execute(query, (
                candidate_id,
                edu.get('degree', ''),
                edu.get('institution_name', ''),
                year
            ))
        return True
    except Error as e:
        st.error(f"Error saving education: {e}")
        return False


def insert_work_experience_data(cursor, candidate_id, work_experience_data):
    """
    Insert work experience records with experience calculation.
    Handles date parsing and experience calculation.
    """
    try:
        query = """INSERT INTO WorkExperience 
                (candidate_id, position, company, years_experience, description) 
                VALUES (?, ?, ?, ?, ?)"""

        for work in work_experience_data:
            sdt = work.get("start_date")
            edt = work.get("end_date")
            experience = 0

            try:
                # Parse start date
                sdt = datetime.datetime.strptime(sdt, '%Y-%m-%d') if sdt else None

                # Handle end date special cases
                if str(edt).lower() in ["current", "present", "not available"]:
                    edt = datetime.datetime.now()
                else:
                    edt = datetime.datetime.strptime(edt, '%Y-%m-%d') if edt else None

                # Calculate years experience
                if sdt and edt:
                    delta = relativedelta(edt, sdt)
                    experience = delta.years + delta.months / 12  # More precise calculation

            except (ValueError, TypeError) as e:
                st.warning(f"Invalid date format: {e}")
                experience = 0

            cursor.execute(query, (
                candidate_id,
                work.get('position', ''),
                work.get('company_name', ''),
                round(experience, 1),  # Store as decimal with 1 decimal place
                work.get('description', '')
            ))
        return True
    except Error as e:
        st.error(f"Error saving work experience: {e}")
        return False


def insert_skills_data(cursor, candidate_id, skills_data):
    """
    Insert candidate skills with error handling.
    Skips empty skill names.
    """
    try:
        query = """INSERT INTO Skills (candidate_id, skill_name) 
                VALUES (?, ?)"""

        for skill in skills_data:
            skill_name = skill.get('skill_name', '').strip()
            if skill_name:  # Skip empty skills
                cursor.execute(query, (candidate_id, skill_name))
        return True
    except Error as e:
        st.error(f"Error saving skills: {e}")
        return False