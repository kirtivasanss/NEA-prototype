import streamlit as st
from add_page import addPage
from signupPage import signupPage
from viewpage import viewPage
from test2 import searchPage
from account_page import accountPage

pages = st.navigation([st.Page(signupPage),st.Page(viewPage),st.Page(addPage), st.Page(searchPage),st.Page(accountPage)])
pages.run()
