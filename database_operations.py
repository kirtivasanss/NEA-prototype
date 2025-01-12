import streamlit as st
import mysql.connector
from mysql.connector import Error
from dateutil.relativedelta import relativedelta
import datetime

@st.cache_resource
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Emug123$",
            database = "ResumeDatabase"
        )
        if connection.is_connected():
            print("Connected to MySQL server")
            return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None



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


def insert_candidate_data(cursor, candidate_data):
    cursor.execute("USE ResumeDatabase;")
    """Insert data into the Candidates table."""
    query = """INSERT INTO Candidates (name, email, phone_number, location) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        phone_number = VALUES(phone_number),
        location = VALUES(location)"""
    cursor.execute(query, (
        candidate_data['name'],
        candidate_data['email'],
        candidate_data['phone_number'],
        candidate_data['location']
    ))
    return cursor.lastrowid


def insert_education_data(cursor, candidate_id, education_data):
    cursor.execute("USE ResumeDatabase;")
    """Insert data into the Education table."""
    query = """ INSERT INTO Education (candidate_id, degree, institution, graduation_year) 
                VALUES (%s, %s, %s, %s)"""
    for edu in education_data:
        try:
            dt = datetime.datetime.strptime(edu['end_date'], '%Y-%m-%d')
            year = str(dt.year)
        except Exception as e:
            year = "Not Available"

        cursor.execute(query, (
            candidate_id,
            edu['degree'],
            edu['institution_name'],
            year
        ))


def insert_work_experience_data(cursor, candidate_id, work_experience_data):
    cursor.execute("USE ResumeDatabase;")

    query = """ INSERT INTO WorkExperience (candidate_id, position, company, years_experience, description) 
                VALUES (%s, %s, %s, %s, %s)"""
    for work in work_experience_data:
        # Calculating Years of experience using dates
        sdt = work["start_date"]
        edt = work["end_date"]
        sdt = datetime.datetime.strptime(sdt,'%Y-%m-%d')

        try:
            if edt == "Current" or edt == "Present":
                edt = datetime.datetime.today()
            else:
                edt = datetime.datetime.strptime(edt,'%Y-%m-%d')

            experience = str(relativedelta(edt, sdt).years)

        except Exception as e:
            experience = "Not Available"

        cursor.execute(query, (
            candidate_id,
            work['position'],
            work['company_name'],
            experience,
            work['description']
        ))


def insert_skills_data(cursor, candidate_id, skills_data):
    cursor.execute("USE ResumeDatabase;")
    """Insert data into the Skills table."""
    query = """ INSERT INTO Skills (candidate_id, skill_name) 
                VALUES (%s, %s)"""
    for skill in skills_data:
        cursor.execute(query, (
            candidate_id,
            skill['skill_name']
        ))
