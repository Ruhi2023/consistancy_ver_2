import streamlit as st
import Consistancy_tables_with_orm as su
from utilities import Authentication

def save_in_session_state(authenticated_user):
    st.session_state["authenticated_user"] = authenticated_user
# login utility to actually authenticate the user and get authenticated_user in streamlit session state
def make_database_call_to_login(username, password):
    auth = Authentication()
    check_res = auth.check_user(username, password)
    if check_res["status"].lower() == "success":
        st.success("User authenticated successfully")
        save_in_session_state(check_res["user"])
        auth.update_last_login(check_res["user"].user_id)
        # return check_res["user"], True
    else:
        # return check_res["user"], False
        st.error("User authentication failed")



def login_user(username, password):
    # st.success(f"Login button clicked, got username = {username} and password = {password}")
    if not username == "" or not password == "":
         make_database_call_to_login(username, password)
        # st.success("Login successful")
    else:
        st.error("Login failed \n\n Username or password is incorrect")


st.title("Login")

with st.form(key="login_form"):
    username = st.text_input("Username")
    # print(username)
    password = st.text_input("Password", type="password")
    # print(password)
    submit_button = st.form_submit_button("Login", on_click=login_user, args=(username, password))

