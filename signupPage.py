import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


# Save user credentials to a separate YAML file
def save_credentials(file_path, credentials):
    with open(file_path, "w") as file:
        yaml.dump(credentials, file, default_flow_style=False)


def add_user(credentials, username, name, email, password):
    hashed_password = stauth.Hasher([password]).generate()[0]
    config["credentials"]["username"][username] = {
        "name": name,
        "email": email,
        "password": hashed_password,
    }
    return credentials


# Load credentials from the file
with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    # Create an authenticator instance
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Sign Up"])

if page == "Login":
    # --- Login Page ---
    st.title("Login")

    # Debug: Print the loaded credentials

    # Login logic
    authenticator.login()

    if st.session_state['authentication_status']:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        st.title('Some content')
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')

    if st.session_state['authentication_status']:
        try:
            if authenticator.reset_password(st.session_state['username']):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)


elif page == "Sign Up":
    # --- Sign Up Page ---
    st.title("Create a New Account")

    email_of_registered_user, \
        username_of_registered_user, \
        name_of_registered_user = authenticator.register_user()
    if email_of_registered_user:
        st.success('User registered successfully')
