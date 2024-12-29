import streamlit as st
from candidate import Candidate

class CandidateInfoApp:
    def display_candidate_info(self,candidate):
        """
        Display a styled, clickable card for the candidate with their information.
        """
        # Define a unique key for each card using candidate_id
        unique_key = f"card_{candidate.candidate_id or candidate.name.replace(' ', '_')}"

        # Make the card clickable using an invisible link styled as a card
        card_html = f"""
        <a href="?selected_candidate_id={candidate.candidate_id}" style="text-decoration: none; color: inherit;">
            <div style=" 
                border-radius: 10px; 
                padding: 15px; 
                margin-bottom: 20px; 
                background-color: #262730;
                box-shadow: 0 8px 20px #393A48;
                transition: transform 0.2s;
            " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                <h3 style="margin: 5px; color:  ;">{candidate.name}</h3>
                <p style="margin: 5px 0 0; color: #FAFAFA;">📧 {candidate.email}</p>
                <p style="margin: 5px 0 0; color: #FAFAFA;">📞 {candidate.phone}</p>
                <p style="margin: 5px 0 0; color: #FAFAFA;">📍 {candidate.location}</p>
            </div>
        </a>
        """
        # Render the card
        st.markdown(card_html, unsafe_allow_html=True)

