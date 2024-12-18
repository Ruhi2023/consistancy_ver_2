import google.generativeai as genai
import streamlit as st
import datetime as dt
import mysql.connector as conn
import os
import Consistancy_tables as su

# seg-expl initialization

my_host,my_user,pswd,dbname = su.getconnnames()
def get_mykey():
    found = 0
    dir_per =""
    for dirpath, dirnames, filenames in os.walk(os.getcwd()):
        if "api_key.txt" in filenames:
            found = 1
            dir_per = dirpath
            break
    if found == 1:
        with open(os.path.join(dir_per, "api_key.txt")) as f:
            api_k = f.readlines()
        return api_k[0].replace("\n","")
    else:
        st.error("No api_key.txt found")
        st.stop()
        return None
api_key_from_func = get_mykey()
if api_key_from_func is None:
    st.error("No api_key.txt found in the current directory.\n Please make sure that api_key.txt is present in the current directory")
    st.stop()
else:
    genai.configure(api_key=api_key_from_func)
# st.write(st.session_state)
# generate Questions based on topic 
# make a form to ask for these answers 


if not "project" in st.session_state:
    st.write("Go to main app and generate topic")
    st.page_link( "pages/Main_app.py",label="Go to main app",icon="🏠")
# w-flow # workflow
# w-flow # form to generate test-> generate questions -> get answers -> evaluate -> store in database
# w-flow # form output in st.session_state


# * form here will include: test my understanding (summary generated by test_results), test my workflow (summary_generated by test results), improve my_workflow
# * test my workflow is to understand waht i did for it it is similar to ask my workflow regardless Questions and answers need to be stored somewhere
# todo: change the db_table my_progress
# ? need to account for if it is testing understanding or workflow

# * session_state details name will br p_test_details 
# 1. create test for both understanding and workflow
    # 1.1 UI create form to take in tests 
    # 1.2 function to store test in database (here update st.session state_to generate Questions) return a dict to store in st.session_state.ptest_details
    # 1.3 store dict on ptest_details
# 2. generate and display questions for both understanding and workflow 
    # 2.1 call the generate functions method, pass which prompts to be used,
    # 2.2 store in database
    # 2.3 format data as 2 dicts one for workflow Questions another for test_of_understanding_questions
    # 2.4 make 2 colmns and side by side generate forms 
    # 2.5 evalutae individul questions and workflow add to db
# 3. evaluation of both understanding and workflow and results to their respective dbs 
    # 3.1 generate results evaluation and score them
    # 3.2 store in a markdown file
# 4. generate and store overall result








# seg-expl start of execution
    # 1.2 function to store test in database (here update st.session state_to generate Questions) return a dict to store in st.session_state.ptest_details
def store_test_project_in_db(eno,mno,hno,tp_id,tp_name,wrkflow_qs):
    pass
# 1. create test for both understanding and workflow
    # 1.1 UI create form to take in tests 
# // with st.form("project evaluation form"):
with st.form("project evaluation form generate test"):
    the_db = conn.connect(
        host = my_host,
        user = my_user,
        passwd = pswd,
        database = dbname
    )
    the_cur = the_db.cursor()
    the_cur.execute("select topic_id, topic_name from topics where topic_type = 'projects' or topic_type = 'ideas_implementation' ")
    projects_names = the_cur.fetchall()
    the_cur.close()
    the_db.close()
    if len(projects_names) == 0:
        st.warning("No implementations added yet")
        projects_names = [""]
    specific_project = st.selectbox("Select project",projects_names)
    # test of understanding
    easy_num = st.number_input("Tell the number of esay Questions",min_value=0, max_value=5)
    mid_num = st.number_input("Tell the number of Medium Questions", min_value=0, max_value=5)
    hard_num = st.number_input("Tell the number of Hard Questions", min_value=0, max_value=5)
    if sum([easy_num,mid_num,hard_num]) <= 4:
        st.warning("Please selects atleast 5 questions from any difficulty level")
    
    #workflow Questions
    wrkflow_questions = st.number_input("Tell the number of Questions you can answer for wrokflow", min_value=6, max_value=21, help="It's the number of Questions you will be asked regarding your specific implementation of the practical project, choose more for complex projects")
    submit_btn = st.form_submit_button("Generate Test")
    if submit_btn:
        st.session_state.p_test_details = store_test_project_in_db(eno=easy_num, mno=mid_num, hno=hard_num, tp_id=specific_project[0], tp_name=specific_project[1], wrkflow_qs=wrkflow_questions)
        st.session_state.gen_QS_wf_un = True
        a=0

