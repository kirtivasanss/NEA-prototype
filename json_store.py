import os
import json
from database_operations import *
from glob import glob


def reset():
    files = glob('temp/*')
    for f in files:
        os.remove(f)


def store_json():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        file_group = glob("/Users/kirti/Python_Projects/NEA FULL/temp/*.json")

        print(file_group)
        for file in file_group:
            if 'candidate' in file.lower():
                with open(f'{file}', 'r') as f:
                    candidate_data = json.load(f)
                print("loaded candidate")
            elif 'education' in file.lower():
                with open(f'{file}', 'r') as f:
                    education_data = json.load(f)
                print("loaded education")
            elif 'experience' in file.lower():
                with open(f'{file}', 'r') as f:
                    work_experience_data = json.load(f)
                print("loaded experience")
            elif 'skills' in file.lower():
                with open(f'{file}', 'r') as f:
                    skills_data = json.load(f)
                print("loaded skills")

        print(candidate_data)
        print(education_data)
        print(work_experience_data)
        print(skills_data)

    # Check if candidate data exists before proceeding

        candidate_id = insert_candidate_data(cursor, candidate_data)
        print("candidate")

    # Insert education data if available

        insert_education_data(cursor, candidate_id, education_data)
        print("aEdu")

    # Insert work experience data if available

        insert_work_experience_data(cursor, candidate_id, work_experience_data)
        print("expo")

    # Insert skills data if available

        insert_skills_data(cursor, candidate_id, skills_data)
        print("skills")

    except Exception as err:
        connection.rollback()
        print(f"Error occurred: {err}")

    connection.commit()

    reset()

