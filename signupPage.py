import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import re

# Hide the sidebar for unauthenticated pages.
st.markdown("<style>div[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

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

def validate_email(email):
    """
    Validate email format using regex.
    Returns boolean.
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_username(username):
    """
    Validate username format using regex.
    Returns (is_valid, message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, "Username is valid"

def load_auth_config():
    """Load authentication configuration from a YAML file."""
    with open('credentials.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def save_auth_config(config):
    """Save authentication configuration to a YAML file."""
    with open('credentials.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def signupPage():
    # If the user is already authenticated, prevent access to this page.
    if st.session_state.get('authentication_status'):
        st.success(f"You are already logged in as {st.session_state.get('name', 'User')}!")
        st.stop()

    # Custom CSS for styling tabs and form container.
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
        }
        .auth-form {
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)

    # Load the authentication configuration.
    config = load_auth_config()

    # Create the authenticator object.
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

    # Create tabs for login, registration, and account management.
    auth_options = st.tabs(["🔑 Login", "📝 Register", "🔄 Account Management"])

    # --- Login Tab ---
    with auth_options[0]:
        st.markdown("### Welcome Back! 👋")
        authenticator.login("main")
        if st.session_state.get("authentication_status"):
            st.success(f"Welcome back, {st.session_state.get('name', 'User')}!")
            authenticator.logout("Logout", "main", key="unique_key")
        elif st.session_state.get("authentication_status") == False:
            st.error("Username/password is incorrect")

    # --- Register Tab ---
    with auth_options[1]:
        st.markdown("### Create New Account 📋")
        with st.expander("Password Requirements", expanded=st.session_state['show_password_requirements']):
            st.info("""
            Your password must contain:
            - At least 8 characters
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one number
            - At least one special character (!@#$%^&*(),.?":{}|<>)
            """)
        with st.form("registration_form"):
            email = st.text_input("Email")
            username = st.text_input("Username")
            name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")
            if submit:
                # Validate email
                if not validate_email(email):
                    st.error("Please enter a valid email address")
                    return
                # Validate username
                username_valid, username_msg = validate_username(username)
                if not username_valid:
                    st.error(username_msg)
                    return
                # Validate password
                password_valid, password_msg = validate_password(password)
                if not password_valid:
                    st.error(password_msg)
                    st.session_state['show_password_requirements'] = True
                    st.experimental_rerun()
                    return
                # Check password confirmation
                if password != password_confirm:
                    st.error("Passwords do not match")
                    return
                # Attempt registration
                try:
                    if authenticator.register_user("main"):
                        st.success("Registration successful! Please log in.")
                        save_auth_config(config)
                except Exception as e:
                    st.error(str(e))

    # --- Account Management Tab ---
    with auth_options[2]:
        st.markdown("### Account Management")
        with st.expander("Reset Password", expanded=True):
            if st.session_state.get("authentication_status"):
                try:
                    if authenticator.reset_password(st.session_state['username'], "main"):
                        st.success("Password modified successfully")
                        save_auth_config(config)
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Please log in to reset your password")
        with st.expander("Update Profile", expanded=True):
            if st.session_state.get("authentication_status"):
                try:
                    if authenticator.update_user_details(st.session_state['username'], "main"):
                        st.success("Profile updated successfully")
                        save_auth_config(config)
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Please log in to update your profile")

if __name__ == '__main__':
    signupPage()
