import streamlit as st
import Consistancy_tables as su



# login utility to actually authenticate the user and get authenticated_user in streamlit session state
def make_database_call_to_login(username, password):
    db,cur = su.connnecting()
    cur.execute("select id,name,passwd from users where username = %s and passwd = %s", (username, password))
    res = cur.fetchone() 
    if res is not None:
        return True,res[0],res[1]
    else:
        return False,-1,-1

def save_in_session_state(authenticated_user):
    st.session_state.authenticated_user = authenticated_user

def login_user(username, password):
    authenticated_user = make_database_call_to_login(username, password)
    if authenticated_user[0]:
        save_in_session_state(authenticated_user)
        st.success("Login successful")
    else:
        st.error("Login failed \n\n Username or password is incorrect")
st.title("Login")

with st.form(key="login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit_button = st.form_submit_button("Login", on_click=login_user, args=(username, password))

