import mysql.connector

# Establish connection to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Emug123$",
    database="ResumeDatabase"
)

cursor = mydb.cursor()


def fetch_candidate_data(cursor, candidate_id):
    query = """
    SELECT candidate_id, name, email, phone_number, location FROM Candidates
    WHERE candidate_id = %s
    """
    cursor.execute(query, (candidate_id,))
    return cursor.fetchall()

def fetch_education_data(cursor, candidate_id):
    query = """
    SELECT degree, institution, graduation_year FROM Education
    WHERE candidate_id = %s
    """
    cursor.execute(query, (candidate_id,))
    return cursor.fetchall()

def fetch_experience_data(cursor, candidate_id):
    query = """
    SELECT position, company, years_experience, description FROM WorkExperience
    WHERE candidate_id = %s
    """
    cursor.execute(query, (candidate_id,))
    return cursor.fetchall()

def fetch_skills_data(cursor, candidate_id):
    query = """
    SELECT skill_name FROM Skills
    WHERE candidate_id = %s
    """
    cursor.execute(query, (candidate_id,))
    return cursor.fetchall()

def fetch_feedback_data(cursor, candidate_id):
    query = """
    SELECT feedback, reviewer FROM CandidateFeedback
    WHERE candidate_id = %s
    """
    cursor.execute(query, (candidate_id,))
    return cursor.fetchall()
def fetch_multiple_candidate_details(cursor, candidate_ids):
    """
    Given a list of candidate_ids, this function retrieves data from
    all related tables and returns a 3D array where each outer list
    corresponds to a candidate. Each candidate's details are stored
    as a list of arrays from the Candidates, Education, WorkExperience,
    Skills, and CandidateFeedback tables, respectively.
    """
    results = []
    for candidate_id in candidate_ids:
        candidate_details = []
        candidate_details.append(fetch_candidate_data(cursor, candidate_id))
        candidate_details.append(fetch_education_data(cursor, candidate_id))
        candidate_details.append(fetch_experience_data(cursor, candidate_id))
        candidate_details.append(fetch_skills_data(cursor, candidate_id))
        candidate_details.append(fetch_feedback_data(cursor, candidate_id))
        results.append(candidate_details)
    return results

# Example usage: fetching details for candidate IDs 1, 2, and 3


cursor.execute("SELECT * FROM ResumeEmbeddings")
x = cursor.fetchall()

print(x)