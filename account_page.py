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

def validate_password(password):
    """
    Validate password strength using regex.
    Returns (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password meets requirements"

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
    # Initialize session state values.
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'show_password_requirements' not in st.session_state:
        st.session_state['show_password_requirements'] = False


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

        if st.session_state['authentication_status']:
            with st.expander("Password Requirements", expanded=st.session_state['show_password_requirements']):
                st.info("""
                Your password must contain:
                - At least 8 characters
                - At least one uppercase letter
                - At least one lowercase letter
                - At least one number
                - At least one special character (!@#$%^&*(),.?":{}|<>)
                """)

            try:
                if authenticator.reset_password(st.session_state['username']):
                    save_auth_config(config)
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)

    with account_tabs[1]:
        st.subheader("Update Profile")
        # Provide a button to update user details

        if st.session_state['authentication_status']:
            try:
                if authenticator.update_user_details(st.session_state['username']):
                    save_auth_config(config)
                    st.success('Entries updated successfully')
            except Exception as e:
                st.error(e)

if __name__ == '__main__':
    accountPage()
