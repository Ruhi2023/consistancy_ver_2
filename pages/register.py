import streamlit as st
import Consistancy_tables_with_orm as db
from hashlib import sha256
import re
from utilities import Authentication
# make a registration form 
sess = db.create_session()

def check_password_strength(password):
    # check if password is strong enough
    pattern = r'^(?!.*&u)(?!.*\s)(?=(?:.*[A-Z]){2,})(?=.*\d)(?=.*[^A-Za-z0-9]).{8,16}$'
    if bool(re.match(pattern, password)):
        return True
    else:
        st.error("Password must be at least 8 characters long and contain at least 2 uppercase letters, a number, and a special character")
        return False
def check_username(username):
    # check if username is unique
    try:
        res = sess.query(db.User).filter(db.User.username == username).first()
        if res is not None:
            st.error("Username already exists")
        elif bool(re.match(r'^[a-zA-Z0-9_]*$', username)):
            return True
    except Exception as e:
        st.error(f"An exception occured while checking username: {e}")
        return False
def handle_register(name,username, password):
    if check_username(username) and check_password_strength(password):
        auth = Authentication()
        try:
            auth.add_user_to_database(name, username, password)
            st.success("User added to database Now goto login page")
        except Exception as e:
            st.error(f"An exception occured while adding user to database: {e}")
    else:
        st.error("Invalid username or password")


st.title("Register")

with st.form(key="register_form"):
    name = st.text_input("Name", help="Name can be anything")
    username = st.text_input("Username", help="Username must be unique")
    password = st.text_input("Password", type="password", help="Password must be at least 8 characters long")
    submit_button = st.form_submit_button("Register", on_click=handle_register, args=(name,username, password))