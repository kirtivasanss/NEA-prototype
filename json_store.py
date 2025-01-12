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
        for file in file_group:
            if 'candidate' in file.lower():
                with open(f'{file}', 'r') as f:
                    candidate_data = json.load(f)
            elif 'education' in file.lower():
                with open(f'{file}', 'r') as f:
                    education_data = json.load(f)

            elif 'experience' in file.lower():
                with open(f'{file}', 'r') as f:
                    work_experience_data = json.load(f)

            elif 'skills' in file.lower():
                with open(f'{file}', 'r') as f:
                    skills_data = json.load(f)



    # Check if candidate data exists before proceeding

        candidate_id = insert_candidate_data(cursor, candidate_data)

    # Insert education data if available

        insert_education_data(cursor, candidate_id, education_data)

    # Insert work experience data if available

        insert_work_experience_data(cursor, candidate_id, work_experience_data)

    # Insert skills data if available

        insert_skills_data(cursor, candidate_id, skills_data)

        reset()

        connection.commit()
    except Exception as err:
        print(f"Error occurred: {err}")




