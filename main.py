import streamlit as st
from add_page import addPage
from signupPage import signupPage
from viewpage import viewPage
from search_page import searchPage
from account_page import accountPage
from database_operations import create_tables,create_connection

connection = create_connection
cursor = connection.cursor()

create_tables(cursor)

pages = st.navigation(
    [
       st.Page(signupPage, title="Login"),
       st.Page(viewPage,title="View Candidates"),
       st.Page(addPage,title="Add Candidates"),
       st.Page(searchPage,title="Search Page"),
       st.Page(accountPage,title="Account Page")
    ]
)
pages.run()
