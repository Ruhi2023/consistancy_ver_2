import streamlit as st
import time
import Consistancy_tables_with_orm as su
import re
# Initialize session state variables



st.session_state
# Function to add project
def add_project(name, topic, description):
    name = name.replace(" ", "_")
    topic = topic.replace(" ", "_")
    description = description.replace(" ", "_")
    project_topic = name + "_from_" + topic
    db,cur = su.connecting_connector()
    Query = "Insert into topics (topic_name,topic_type, topic_description, user_id) values (%s,%s, %s, %s) returning topic_id"
    type_2 = "projects"
    cur.execute(Query, (project_topic, type_2, description, st.session_state.authenticated_user.user_id))
    db.commit()
    current_topic_id = cur.fetchone()[0]
    st.success("Project added!")
    st.session_state.topic_id_project = current_topic_id
    time.sleep(2)
    st.switch_page("pages/project_evaluation.py")


# Function to add study topic
def add_study(topic):
    topic = topic.replace(" ", "_")
    # check if topic already exists
    db,cur = su.connecting_connector()
    cur.execute("Select count(topic_id) from topics where topic_name = %s", (topic,))
    if cur.fetchone()[0] > 0:
        st.error("Topic already exists!")
        return
    else:
        Query = "Insert into topics (topic_name,topic_type, user_id) values (%s,%s, %s) returning topic_id"
        type_1 = "skills"
        cur.execute(Query, (topic, type_1, st.session_state.authenticated_user.user_id))
        db.commit()
        current_topic_id = cur.fetchone()[0]
        st.success("Study topic added!")
        st.session_state.topic_id_study = current_topic_id
    time.sleep(2)
    st.switch_page("pages/Testing_screen_2_temp.py")

# Function to listen to struggles
def validate_inp(inp_txt,validate_name):
    # Logic for validating input
    if inp_txt == "":
        st.warning("Please enter your {}".format(validate_name))
        return False
    regx_patten = r'^[a-zA-Z0-9& ]*$'
    if validate_name == "project_description":
        regx_patten = r'^.*$'
    val = bool(re.match(regx_patten, inp_txt))
    warning = "Your {} is not in valid format. valid characters are alphabets, digits, and characters '&' and ' ' ".format(validate_name)
    if not val:
        st.warning(warning)
    return val
# Set the title of the app
st.title("What did you do today?")

# Section for Work & Projects
cl1,cl2 = st.columns([1,1])
with cl1:
    st.header("Work & Projects")
    work_projects = st.checkbox("Did you work on any projects?")

    if work_projects:
        with st.form(key='project_form'):
            project_name = st.text_input("Project Name")
            project_topic = st.text_input("Project Topic")
            project_description = st.text_area("What did you do?")
            
            submit_button = st.form_submit_button("Test what i learnt")
            valid = validate_inp(project_topic, "project_topic") and validate_inp(project_description, "project_description") and validate_inp(project_name, "project_name")
        if submit_button and valid:
            add_project(project_name, project_topic, project_description)
            #st.switch_page("Project_based_testing.py")


# Section for Study & Skills
with cl2:
    st.header("Study & Skills")
    study_skills = st.checkbox("Did you study any new skills?")

    if study_skills:
        with st.form(key='study_form'):
            study_topic = st.text_input("What topic did you study?")
            
            study_submit_button = st.form_submit_button("Test my understanding")
            valid = validate_inp(study_topic, "study_topic")
        if study_submit_button and valid:
            add_study(study_topic)

st.markdown("A Quote from my friend:<br> <i><b>\"The greatest glory in living lies not in never falling, but in rising every time we fall.\" </b></i> ", unsafe_allow_html=True)

# Navigation Buttons
st.header("What else?")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Thought of some more ideas"):
        # Here you can define navigation to the ideas page
        st.write("Navigating to Ideas Page...")
        time.sleep(3)
        st.switch_page("pages//Idea_management.py")
        # Implement navigation logic or create a new function/page as needed

with col2:
    if st.button("Listen to my struggles"):
        st.write("Navigating to Chat Page...")
        time.sleep(3)
        st.switch_page("pages/Struggles.py") # Call the function to navigate or listen to struggles

with col3:
    if st.button("Nothing, I need motivation"):
        # Here you can define navigation to the motivation page
        st.write("Navigating to Motivation Page...")
        # Implement navigation logic or create a new function/page as needed
        time.sleep(3)
        st.switch_page("pages/Improv_sug.py")



