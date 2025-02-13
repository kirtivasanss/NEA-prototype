import streamlit as st
import mysql.connector
from mysql.connector import Error
from dateutil.relativedelta import relativedelta
import datetime

@st.cache_resource
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=st.secrets["database"]["host"],
            user=st.secrets["database"]["user"],
            password=st.secrets["database"]["password"],
            database = st.secrets["database"]["database"]
        )

        if connection.is_connected():
            print("Connected to MySQL server")
            return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def create_tables(connection):
    """
    Create tables in SQLite database with proper schema and relationships.
    Includes error handling for table creation failures.
    """
    cursor = connection.cursor()
    # Define table schemas using SQLite syntax
    tables = [
        """CREATE TABLE IF NOT EXISTS Candidates (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS Education (
            education_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            degree TEXT,
            institution TEXT,
            graduation_year INTEGER,  -- SQLite doesn't have YEAR type
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS WorkExperience (
            work_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            position TEXT,
            company TEXT,
            years_experience INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS Skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            skill_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS ResumeEmbeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            embedding TEXT NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE CandidateFeedback (
            feedback_id INT PRIMARY KEY AUTO_INCREMENT,
            candidate_id INT,
            feedback TEXT NOT NULL,
            reviewer VARCHAR(255) NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )"""
    ]
    for table in tables:
        try:
            cursor.execute(table)
        except Exception as err:
            print(f"Failed to create table: {err}")
    cursor.commit()

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
            CONCAT(w.position, ' at ', w.company, ' (', w.years_experience, ' years), desc', w.description) 
            SEPARATOR '; ') AS work_experience,
        GROUP_CONCAT(DISTINCT 
            CONCAT(s.skill_name, ' ') 
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
            CONCAT(s.skill_name, ' ') 
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
    query = """
        INSERT INTO Candidates (name, email, phone_number, location) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            phone_number = VALUES(phone_number),
            location = VALUES(location),
            candidate_id = LAST_INSERT_ID(candidate_id)
    """
    cursor.execute(query, (
        candidate_data['name'],
        candidate_data['email'],
        candidate_data['phone_number'],
        candidate_data['location']
    ))
    candidate_id = cursor.lastrowid

    # If candidate_id is not properly set (i.e., update occurred and lastrowid is 0 or None), fetch it manually.
    if not candidate_id:
        cursor.execute("SELECT candidate_id FROM Candidates WHERE email = %s", (candidate_data['email'],))
        result = cursor.fetchone()
        if result:
            candidate_id = result[0]
        else:
            raise Exception("Candidate record was not found after insert/update.")

    return candidate_id


def insert_education_data(cursor, candidate_id, education_data):
    cursor.execute("USE ResumeDatabase;")
    # Insert data into the Education table.
    query = """INSERT INTO Education (candidate_id, degree, institution, graduation_year) 
               VALUES (%s, %s, %s, %s)"""
    for edu in education_data:
        try:
            # Check if the end_date indicates that education is current.
            if edu['end_date'] in ["Current", "Present", "Not Available"]:
                year = datetime.datetime.today().year
            else:
                dt = datetime.datetime.strptime(edu['end_date'], '%Y-%m-%d')
                year = dt.year
        except Exception as e:
            # In case of any exception, default to year 0.
            year = 0

        cursor.execute(query, (
            candidate_id,
            edu['degree'],
            edu['institution_name'],
            year
        ))


def insert_work_experience_data(cursor, candidate_id, work_experience_data):
    cursor.execute("USE ResumeDatabase;")
    # Insert data into the WorkExperience table.
    query = """INSERT INTO WorkExperience (candidate_id, position, company, years_experience, description) 
               VALUES (%s, %s, %s, %s, %s)"""
    for work in work_experience_data:
        # Convert start_date to a datetime object.
        sdt = datetime.datetime.strptime(work["start_date"], '%Y-%m-%d')
        try:
            # Check if the end_date indicates current employment.
            if work["end_date"] in ["Current", "Present", "Not Available"]:
                edt = datetime.datetime.today()
            else:
                edt = datetime.datetime.strptime(work["end_date"], '%Y-%m-%d')
            # Calculate the number of full years of experience.
            experience = relativedelta(edt, sdt).years
        except Exception as e:
            # In case of error, default to 0 years of experience.
            experience = 0

        cursor.execute(query, (
            candidate_id,
            work['position'],
            work['company_name'],
            experience,
            work['description']
        ))


def insert_skills_data(cursor, candidate_id, skills_data):
    cursor.execute("USE ResumeDatabase;")
    # Insert data into the Skills table.
    query = """INSERT INTO Skills (candidate_id, skill_name) 
               VALUES (%s, %s)"""
    for skill in skills_data:
        cursor.execute(query, (
            candidate_id,
            skill['skill_name']
        ))


def insert_feedback(cursor ,candidate_id, feedback, reviewer):
    query = """
    INSERT INTO CandidateFeedback (candidate_id, feedback, reviewer) 
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (candidate_id, feedback, reviewer))


def delete_candidate(cursor,candidate_id):
    """
    Delete a candidate (and all related records via cascade) from the database.

    Args:
        candidate_id (int): The unique identifier of the candidate.
    """
    try:
        delete_query = "DELETE FROM Candidates WHERE candidate_id = %s"
        cursor.execute(delete_query, (candidate_id,))
        if cursor.rowcount > 0:
            print("Candidate deleted successfully.")
        else:
            print("Candidate not found.")
    except mysql.connector.Error as err:
        print(f"Error deleting candidate: {err}")
        cursor.rollback()
        raise


def update_candidate(candidate_id, name, email, phone_number, location):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE Candidates
            SET name = %s, email = %s, phone_number = %s, location = %s
            WHERE candidate_id = %s
        """
        cursor.execute(query, (name, email, phone_number, location, candidate_id))
        conn.commit()
        st.success("Candidate updated successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error updating candidate: {err}")
    finally:
        cursor.close()
        conn.close()


def update_education(education_id, candidate_id, degree, institution, graduation_year):
    conn = create_connection
    cursor = conn.cursor()
    try:
        query = """
            UPDATE Education
            SET candidate_id = %s, degree = %s, institution = %s, graduation_year = %s
            WHERE education_id = %s
        """
        cursor.execute(query, (candidate_id, degree, institution, graduation_year, education_id))
        conn.commit()
        st.success("Education record updated successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error updating education: {err}")
    finally:
        cursor.close()
        conn.close()


def update_work_experience(work_id, candidate_id, position, company, years_experience, description):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE WorkExperience
            SET candidate_id = %s, position = %s, company = %s, years_experience = %s, description = %s
            WHERE work_id = %s
        """
        cursor.execute(query, (candidate_id, position, company, years_experience, description, work_id))
        conn.commit()
        st.success("Work experience record updated successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error updating work experience: {err}")
    finally:
        cursor.close()
        conn.close()


def update_skill(skill_id, candidate_id, skill_name):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE Skills
            SET candidate_id = %s, skill_name = %s
            WHERE skill_id = %s
        """
        cursor.execute(query, (candidate_id, skill_name, skill_id))
        conn.commit()
        st.success("Skill updated successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error updating skill: {err}")
    finally:
        cursor.close()
        conn.close()


def update_resume_embedding(embedding_id, candidate_id, embedding):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE ResumeEmbeddings
            SET candidate_id = %s, embedding = %s
            WHERE id = %s
        """
        cursor.execute(query, (candidate_id, embedding, embedding_id))
        conn.commit()
        st.success("Resume embedding updated successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error updating resume embedding: {err}")
    finally:
        cursor.close()
        conn.close()


def update_candidate_feedback(feedback_id, candidate_id, feedback, reviewer):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE CandidateFeedback
            SET candidate_id = %s, feedback = %s, reviewer = %s
            WHERE feedback_id = %s
        """
        cursor.execute(query, (candidate_id, feedback, reviewer, feedback_id))
        conn.commit()
        st.success("Candidate feedback updated successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error updating candidate feedback: {err}")
    finally:
        cursor.close()
        conn.close()





