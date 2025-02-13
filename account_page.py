import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import re

def load_auth_config():
    """Load authentication configuration from a YAML file."""
    with open("credentials.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def save_auth_config(config):
    """Save authentication configuration to a YAML file."""
    with open("credentials.yaml", "w") as file:
        yaml.dump(config, file, default_flow_style=False)

def accountPage():
    # Load authentication configuration and initialize the authenticator
    config = load_auth_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )

    # If the user is not logged in, stop execution and ask for login
    if not st.session_state.get("authentication_status"):
        st.error("Please log in to access your account.")
        st.stop()

    st.title("Account Page")
    st.write(f"Welcome, {st.session_state.get('name', 'User')}!")

    # Logout button: Immediately logs the user out when clicked
    if st.button("Logout"):
        authenticator.logout("Logout", "main", key="unique_key")
        st.session_state["authentication_status"] = False
        st.rerun()

    # Create tabs for account management functionalities
    account_tabs = st.tabs(["Reset Password", "Update Profile"])

    with account_tabs[0]:
        st.subheader("Reset Password")
        # Provide a button to reset the password
        if st.button("Reset Password"):
            try:
                if authenticator.reset_password(st.session_state["username"], "main"):
                    st.success("Password reset successfully!")
                    save_auth_config(config)
            except Exception as e:
                st.error(f"Error resetting password: {e}")

    with account_tabs[1]:
        st.subheader("Update Profile")
        # Provide a button to update user details
        if st.button("Update Profile"):
            try:
                if authenticator.update_user_details(st.session_state["username"], "main"):
                    st.success("Profile updated successfully!")
                    save_auth_config(config)
            except Exception as e:
                st.error(f"Error updating profile: {e}")

if __name__ == '__main__':
    accountPage()
