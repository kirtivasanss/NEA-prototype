import streamlit as st
from candidate import Candidate

def display_full_candidate_details(candidate):
    """
    Display the full details of a candidate on a separate page with styled tags for skills.
    """
    st.title(f"Details for {candidate['name']}")

    # Candidate details
    st.write(f"📧 **Email:** {candidate['email']}")
    st.write(f"📞 **Phone:** {candidate['phone_number']}")
    st.write(f"📍 **Location:** {candidate['location']}")

    st.markdown("---")

    # Education
    st.subheader("🎓 Education")
    st.write(candidate.get("education", "No education details available."))

    st.markdown("---")

    # Work Experience
    st.subheader("💼 Work Experience")
    st.write(candidate.get("work_experience", "No work experience available."))

    st.markdown("---")

    # Skills as tags
    st.subheader("🛠️ Skills")
    skills = candidate.get("skills", [])
    if skills:
        # Use HTML for styled skill tags
        skills_html = "".join([
            f"""<span style="
            display: inline-block; 
            background-color: #FF4B4B; 
            color: white; 
            padding: 5px 10px; 
            margin: 5px 5px 0 0; 
            border-radius: 15px; 
            font-size: 14px;">{skill}</span>"""
            for skill in skills
        ])
        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.write("No skills available.")
