import streamlit as st

def display_full_candidate_details(candidate):
    """
    Display the full details of a candidate on a separate page with styled tags for skills.
    """

    if candidate:
        # Format skills as a list
        candidate["skills"] = (
            candidate["skills"].split("; ") if candidate.get("skills") else []
        )
        candidate["education"] = (
            candidate["education"].split("; ") if candidate.get("education") else []
        )
        candidate["work_experience"] = (
            candidate["work_experience"].split("; ") if candidate.get("work_experience") else []
        )
    if candidate:
        st.title(f"{candidate['name']}")
    display_info(candidate)

    st.markdown("---")
    if candidate:
        # Education
        st.subheader("🎓 Education")
        education = candidate.get("education", [])
        if education:
            for edu in education:
                degree, institution, year = parse_education_entry(edu)
                display_education(institution,degree,
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
                description= description,
                )
        else:
            st.write("No work experience available.")

        # Skills as tags
        st.subheader("🛠️ Skills")
        skills = candidate.get("skills", [])
        if skills:
            display_skills(skills)
        else:
            st.write("No skills available.")


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
        return exp_entry, "Unknown Company", "Unknown Duration"