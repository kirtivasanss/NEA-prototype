import json
import pypdf
import logging
from datetime import datetime
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
import os

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_agents():
    api_key = "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"
    llm = ChatGroq(
        temperature=0.3,
        model_name="gemma2-9b-it",
        groq_api_key=api_key,
    )

    return [
        Agent(
            role='Resume Data Extractor',
            goal='Extract all required information from the resume',
            backstory="""Expert at parsing resumes and extracting structured information.""",
            verbose=True,
            llm=llm,
            allow_delegation=False
        )
    ]


def create_single_task(agent, resume_text):
    return Task(
        description=f"""Extract all required information from this resume:
        {resume_text}

        Return the data in this EXACT format (replace examples with actual data):
        {{
            "candidate": {{
                "name": "John Doe",
                "email": "john@email.com",
                "phone_number": "123-456-7890",
                "location": "New York, NY"
            }},
            "education": [{{
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "institution_name": "University Name",
                "start_date": "2018-09-01",
                "end_date": "2022-05-31"
            }}],
            "experience": [{{
                "company_name": "Tech Company",
                "position": "Software Engineer",
                "start_date": "2022-06-01",
                "end_date": "2023-12-31",
                "description": "Job description here"
            }}],
            "skills": [{{
                "skill_name": "Python",
                "proficiency": "expert"
            }}]
        }}

        IMPORTANT:
        1. Use ONLY this exact JSON structure
        2. All dates must be in YYYY-MM-DD format
        3. Skill proficiency must be one of: beginner, intermediate, expert
        4. Do not add any additional text or formatting
        """,
        agent=agent,
        expected_output="""{ 
            "candidate": {
                "name": "string",
                "email": "string",
                "phone_number": "string",
                "location": "string"
            },
            "education": [{
                "degree": "string",
                "field_of_study": "string",
                "institution_name": "string",
                "start_date": "string",
                "end_date": "string"
            }],
            "experience": [{
                "company_name": "string",
                "position": "string",
                "start_date": "string",
                "end_date": "string",
                "description": "string"
            }],
            "skills": [{
                "skill_name": "string",
                "proficiency": "string"
            }]
        }"""
    )


def save_json_sections(data, base_filename):
    """Save each section of the parsed resume data as a separate JSON file"""
    # Create output directory if it doesn't exist
    output_dir = 'parsed_resumes'
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save each section separately
    for section in ['candidate', 'education', 'experience', 'skills']:
        if section in data:
            filename = f"{output_dir}/{base_filename}_{section}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data[section], f, indent=4)
            logger.info(f"Saved {section} data to {filename}")


def process_resume(resume_text, base_filename):
    try:
        # Create single agent and task
        agents = create_agents()
        task = create_single_task(agents[0], resume_text)
        crew = Crew(agents=agents, tasks=[task], verbose=True)

        # Get result and parse JSON
        result = crew.kickoff()
        result_str = str(result)

        # Extract JSON from the result
        start_idx = result_str.find('{')
        end_idx = result_str.rfind('}') + 1
        json_str = result_str[start_idx:end_idx]

        # Parse the JSON data
        data = json.loads(json_str)

        # Save the parsed data as separate JSON files
        save_json_sections(data, base_filename)

        return True, "Resume processed successfully"

    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return False, f"Error processing resume: {str(e)}"


def main():
    try:
        logger.info("Starting resume processing")

        # Read PDF file
        pdf_file = 'resume_20241108_132047.pdf'
        base_filename = os.path.splitext(os.path.basename(pdf_file))[0]

        pdf_reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        resume_text = text.strip()

        # Process resume
        success, message = process_resume(resume_text, base_filename)

        if success:
            logger.info("Successfully processed resume")
            print("Successfully processed resume")
        else:
            logger.error(f"Failed to process resume: {message}")
            print(f"Failed to process resume: {message}")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main()