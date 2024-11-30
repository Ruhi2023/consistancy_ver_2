import google.generativeai as genai
import streamlit as st
import datetime as dt
import mysql.connector as conn
import os
import Consistancy_tables as su
from functools import partial

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
# * gegearating a rerun checker
if "p_rerun_ct" not in st.session_state:
    st.session_state.p_rerun_ct = 0
st.session_state.p_rerun_ct += 1

# seg-expl removing the form submitter with last id = anything but rerun ct 
# ! dangerous
for key in st.session_state:
    if key.startswith("FormSubmitter") and not key.endswith(str(st.session_state.p_rerun_ct)) and key != "FormSubmitter:project evaluation form generate test-Generate Test" :
        del st.session_state[key]
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
def store_test_project_in_db(eno,mno,hno,tp_id,tp_name,wrkflow_qs, topic_desc):
    if (eno+mno+hno) <= 4:
        st.warning("Please select atleast 5 questions from any difficulty level, you can aslo select all easy Questions to try out, there is no restriction on it.")
        return 0
    else:
        the_db = conn.connect(
            host = my_host,
            user = my_user,
            passwd = pswd,
            database = dbname
        )
        the_cur = the_db.cursor()
        the_cur.execute("insert into tests (topic_id,easy_Questions,medium_Questions,difficult_Questions) values (%s,%s,%s,%s)",(tp_id,eno,mno,hno))
        test_id_val = the_cur.lastrowid
        the_cur.execute("insert into my_progress (topic_id, test_id, workflow_qs) values (%s,%s,%s)",(tp_id,test_id_val,wrkflow_qs))
        the_db.commit()
        the_cur.close()
        the_db.close()
        ret_d = {"test_id":test_id_val,"topic_id":tp_id,"eno":eno,"mno":mno,"hno":hno, "topic_name":tp_name, "wrkflow_qs":wrkflow_qs, "topic_desc":topic_desc}
        return ret_d
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
    the_cur.execute("select topic_id, topic_name , topic_description from topics where topic_type = 'projects' or topic_type = 'ideas_implementation' ")
    projects_names = the_cur.fetchall()
    the_cur.close()
    the_db.close()
    if len(projects_names) == 0:
        st.warning("No implementations added yet")
        projects_names = [""]
    specific_project = st.selectbox("Select project",projects_names)
    # test of understanding
    easy_num = st.number_input("Tell the number of esay Questions",min_value=0, max_value=10,value=5)
    mid_num = st.number_input("Tell the number of Medium Questions", min_value=0, max_value=10,value=5)
    hard_num = st.number_input("Tell the number of Hard Questions", min_value=0, max_value=10,value=5)
    if sum([easy_num,mid_num,hard_num]) <= 4:
        st.warning("Please selects atleast 5 questions from any difficulty level")
    
    #workflow Questions
    wrkflow_questions = st.number_input("Tell the number of Questions you can answer for wrokflow", min_value=6, max_value=21, help="It's the number of Questions you will be asked regarding your specific implementation of the practical project, choose more for complex projects")
    submit_btn = st.form_submit_button("Generate Test")
    if submit_btn:
        st.session_state.p_test_details = store_test_project_in_db(eno=easy_num, mno=mid_num, hno=hard_num, tp_id=specific_project[0], tp_name=specific_project[1], wrkflow_qs=wrkflow_questions, topic_desc = specific_project[2])
        st.session_state.gen_QS_wf_un = True

def fetch_qs_already_in_db(test_id,topic_id,level):
    my_db = conn.connect(
        host = my_host,
        user = my_user,
        passwd = pswd,
        database = dbname
    )
    my_cur = my_db.cursor()
    if level == "workflow":
        my_cur.execute("select Question from workflow_questions where test_id = %s and topic_id = %s", (test_id,topic_id))
    else:
        my_cur.execute("select Question from questions where test_id = %s and topic_id = %s and question_type = %s", (test_id,topic_id,level))
    questions = my_cur.fetchall()
    my_db.commit()
    my_cur.close()
    my_db.close()
    if len(questions) == 0:
        return "None yet"
    else:
        ste = "Question {Q_num}:"
        ques_db = []
        no = 1
        for q in questions:
            us = ste.format(Q_num=no) + " " + q[0]
            ques_db.append(us)
            no += 1
        return "\n".join(ques_db)

def gen_qs_p_and_store(test_id, topic_id, level, question_no, model_inst):
    topic_name = st.session_state.p_test_details["topic_name"]
    easy_qs_prompt = """I did an activity on the topic of {topic_name}. 
Here is what i did: {topic_desc}.
Ask me specific one (i repeat one) Question about this topic to test my understanding of topic, the Question should be easy to answer, unique and should not be a question about the activity itself.
output only the Question with no additional text or explanation.
avoid duplication with the already generated Questions: {QS_present}""".format(topic_name=topic_name, topic_desc=st.session_state.p_test_details["topic_desc"], QS_present=fetch_qs_already_in_db(test_id=test_id, topic_id=topic_id, level="easy"))
    medium_qs_prompt = """I did an activity on the topic of {topic_name}. 
Here is what i did: {topic_desc}.
Ask me specific one(i repeat one) Question about this topic to test my understanding of topic, the Question should be moderately difficult to answer, unique and should not be a question about the activity itself.
output only the Question with no additional text or explanation.
avoid duplication with the already generated Questions: {QS_present}""".format(topic_name=topic_name, topic_desc=st.session_state.p_test_details["topic_desc"], QS_present=fetch_qs_already_in_db(test_id=test_id, topic_id=topic_id, level="medium"))
    difficult_qs_prompt = """I did an activity on the topic of {topic_name}. 
Here is what i did: {topic_desc}.
Ask me specific one(i repeat one) Question this topic to test my understanding of topic, the Question should be difficult to answer correctly, test in depth knowledge and application (not just surface level understanding), unique and should not be a question about the activity itself.
output only the Question with no additional text or explanation.
avoid duplication with the already generated Questions: {QS_present}""".format(topic_name=topic_name, topic_desc=st.session_state.p_test_details["topic_desc"], QS_present=fetch_qs_already_in_db(test_id=test_id, topic_id=topic_id, level="difficult"))
    wrkflow_qs_prompt = """I did an activity today on the topic of {topic_name}. 
Here is what i did: {topic_desc}.
Ask me specific one(i repeat one) Question about this activity to test my workflow, the questions should specifically ask about the implementation details, intending to probe logical thinking and application of the knowledge.
output only the Question with no additional text or explanation.
Avoid Duplication with the already generated Questions: {QS_present}""".format(topic_name=topic_name, topic_desc=st.session_state.p_test_details["topic_desc"], QS_present=fetch_qs_already_in_db(test_id=test_id, topic_id=topic_id, level="workflow"))
    if level == "easy":
        myprompt = easy_qs_prompt
    elif level == "medium":
        myprompt = medium_qs_prompt
    elif level == "difficult":
        myprompt = difficult_qs_prompt
    else:
        myprompt = wrkflow_qs_prompt
    print(myprompt)
    res = model_inst.generate_content(myprompt)
    m_db = conn.connect(
        host = my_host,
        user = my_user, 
        passwd = pswd,  
        database = dbname)
    m_cur = m_db.cursor()
    if level == "easy"or level == "medium" or level == "difficult":
        m_cur.execute("insert into questions (test_id, topic_id, question_type, question_no, question) values (%s, %s, %s, %s, %s)", (test_id, topic_id, level, question_no, res.text))
    elif level == "workflow":
        m_cur.execute("insert into workflow_questions (test_id, topic_id, question_no, question) values (%s, %s, %s, %s)", (test_id, topic_id, question_no, res.text))
    m_db.commit()
    m_cur.close()
    m_db.close()
    # ?: untested function

def form_dict_for_front(ts_id,tp_id):
    """
    It will return 2 dictionaries
    1 to be used for workflow questions
    structure of dict = {"Question_no": int,
                        "Question": str,
                        "level": "workflow",
                        "Answer": str (it's from user) will be added later}
    2 to be used for unserstanding questions
    structure of dict = {"Question_no": int,
                        "Question": str,
                        "level": str,
                        "Answer": str (it's from user) will be added later}
    """
    my_lis1 = []
    my_lis2 = []
    my_db= conn.connect(
        host = my_host,
        user = my_user, 
        passwd = pswd,  
        database = dbname)
    my_cur = my_db.cursor()
    my_cur.execute("Select Question_no, question from workflow_questions where test_id = %s and topic_id = %s", (ts_id,tp_id))
    my_l1 = my_cur.fetchall()
    my_cur.execute("Select Question_no, question, question_type from questions where test_id = %s and topic_id = %s", (ts_id,tp_id))
    my_l2 = my_cur.fetchall()
    my_db.commit()
    my_cur.close()
    my_db.close()
    for i in my_l1:
        my_lis1.append({"Question_no": i[0],
                        "Question": i[1],
                        "level": "workflow"})
    for i in my_l2:
        my_lis2.append({"Question_no": i[0],
                        "Question": i[1],
                        "level": i[2]})
    st.session_state.p_disp_Qs = True
    return my_lis1, my_lis2

def eval_and_store_pro(d_of_qs_with_ans: dict, model_instance):
    lev = d_of_qs_with_ans["level"]
    if lev == "easy" or lev == "medium" or lev == "difficult":
        prompt_check_question = """Evaluate the answer and just say 1 word correct or incorrect. 
        Remember that the answer has been given in a limited space and is probabilly a summary. 
        The Question: {Question_no}. The answer: {user_answer}""".format(Question_no = d_of_qs_with_ans["Question"], user_answer = d_of_qs_with_ans["user_Answer"])
        prompt_correct_answer_form_model = """The Question: {} \nMy answer: {} \n What did i miss for this answer is incorrect?""".format(d_of_qs_with_ans["Question"], d_of_qs_with_ans["user_Answer"])
        res = model_instance.generate_content(prompt_check_question)
        result = res.text
        if "incorrect" in result or "Incorrect" in result:
            score = 2
            st.error("Your answer is incorrect",icon="😞")
            # write explaination
            explaination = model_instance.generate_content(prompt_correct_answer_form_model)
            st.write(explaination.text)
        elif "correct" in result or "Correct" in result:
            score = 1
            st.success("Your answer is correct! well done!", icon="✅")
        else:
            score = 0
        # * store answer in database
        if score > 0:
            if score == 1:
                correct_answer_bool = True
            if score == 2:
                correct_answer_bool = False
            try:
                my_db_of_qs = conn.connect(
                host = my_host,
                user = my_user,
                passwd = pswd,
                database = dbname)
                my_cur_of_qs = my_db_of_qs.cursor()
                my_cur_of_qs.execute("update questions set user_Answer = %s , correctness = %s where question_no = %s and topic_id = %s and test_id = %s",
                                      (d_of_qs_with_ans["user_Answer"],
                                       correct_answer_bool, 
                                       d_of_qs_with_ans["Question_no"], 
                                       st.session_state.p_test_details["topic_id"], 
                                       st.session_state.p_test_details["test_id"]))
                
            except Exception as e:
                print(d_of_qs_with_ans.keys())
                st.error("Something went wrong while storing the question's answer in database")
                print(dt.datetime.now())
                print(e)
            finally:
                my_db_of_qs.commit()
                my_cur_of_qs.close()
                my_db_of_qs.close()
        
    elif lev == "workflow":
        # seg-expl: just store as it is without checking
        try:
            my_db_of_wf = conn.connect(
            host = my_host,
            user = my_user,
            passwd = pswd,
            database = dbname)
            my_cur_of_wf = my_db_of_wf.cursor()
            my_cur_of_wf.execute("update workflow_questions set User_Answer = %s where Question_no = %s and topic_id = %s and test_id = %s", 
                                (d_of_qs_with_ans["user_Answer"], 
                                 d_of_qs_with_ans["Question_no"], 
                                 st.session_state.p_test_details["topic_id"], 
                                 st.session_state.p_test_details["test_id"]))
        except Exception as e:
            print(d_of_qs_with_ans.keys())
            st.error("Something went wrong while storing workflow answer in database")
            print(dt.datetime.now())
            print(e)
        finally:
            my_db_of_wf.commit()
            my_cur_of_wf.close()
            my_db_of_wf.close()

model_conf = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 20,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=model_conf)
eval_and_store_pro_partial = partial(eval_and_store_pro, model_instance=model)
gen_qs_p_and_store_partial = partial(gen_qs_p_and_store, model_inst=model)
@st.fragment
def display_qs_forms(d_of_qs:dict):
    d_of_qs = d_of_qs
    form_ttl = f"{d_of_qs['level']} Question {d_of_qs['Question_no']}_{st.session_state.p_rerun_ct}"
    with st.form(form_ttl):
        st.markdown("### Level: "+ d_of_qs['level'])
        st.write(d_of_qs['Question'])
        user_ans =st.text_area("Answer")
        sbut = st.form_submit_button(f"Submit {form_ttl}")
        if sbut:
            # ill just return answer and Question no by a function_call
            d_of_qs['user_Answer'] = user_ans
            eval_and_store_pro_partial(d_of_qs)

if "p_test_details" in st.session_state:
    if st.session_state.p_test_details == 0:
        st.warning("Please select atleast 5 questions from any difficulty level")
    if type(st.session_state.p_test_details) == dict and "gen_QS_wf_un" in st.session_state:
        # 2.1 call the generate functions method, pass which prompts to be used,
        total_num_of_questions = st.session_state.p_test_details["eno"] + st.session_state.p_test_details["mno"] + st.session_state.p_test_details["hno"]
        #ill handel progress bar here
        prog = st.progress(0, text="Generating Questions to test understanding")
        progval = 0       
        for i in range(total_num_of_questions):
            if i <= (st.session_state.p_test_details["eno"] -1) :
                level = "easy"
            elif i <= (st.session_state.p_test_details["eno"] + st.session_state.p_test_details["mno"] -1):
                level = "medium"
            else:
                level = "difficult"
            gen_qs_p_and_store_partial(test_id=st.session_state.p_test_details["test_id"], topic_id=st.session_state.p_test_details["topic_id"], level=level, question_no=i+1)
            progval = int(progval + 100/total_num_of_questions)
            prog.progress(progval, text="Generating Questions to test understanding")
        progval = 0
        prog.progress(progval, text="Generating Questions to test workflow")
        for i in range(st.session_state.p_test_details["wrkflow_qs"]):
            gen_qs_p_and_store_partial(test_id=st.session_state.p_test_details["test_id"], topic_id=st.session_state.p_test_details["topic_id"], level="workflow", question_no=i+1)
            progval = int(progval + 100/st.session_state.p_test_details["wrkflow_qs"])
            prog.progress(progval, text="Generating Questions to test workflow")
        st.success(" ALL Questions generated successfully")
        del st.session_state.gen_QS_wf_un
    # ! error prone segment
    Qs_workflow, Qs_understanding = form_dict_for_front(ts_id=st.session_state.p_test_details["test_id"], tp_id=st.session_state.p_test_details["topic_id"])
    if "p_disp_Qs" in st.session_state:
        col1,col2 = st.columns(2)
        with col1:
            st.header("Questions to test workflow")
            for i in range(len(Qs_workflow)):
                display_qs_forms(Qs_workflow[i])
        with col2:
            st.header("Questions to test understanding")
            for i in range(len(Qs_understanding)):
                display_qs_forms(Qs_understanding[i])

st.session_state
# 3. handel evaluations
# done: all Questions are stored in db with their answers, understanding Questions have been stored with correctness as well

# w-flow formatting Questions
def format_qs_and_workflow_ans(test_id, topic_id):
    """
    returns the answers sorted by 
    1. what user did correctly
    2. what user did incorrectly
    3. what user did not answer
    4. the workflow Questions user answer Questions
    """
    prompt_for_wrong_answers = """I took a test on {topic_name}. I got some questions wrong. Please provide for each (i repeat each) question:
1. Correct answer
2. My likely misconception
3. Key study areas or tips to improve
Please format the response in markdown, with each (i repeat each) question starting with a level 3 heading. 
Here are the questions:
"""
    prompt_for_correct_answers = """I took a test on {topic_name} and answered some questions correctly. Please provide for each (i repeat each) question:
1. A more technically detailed and precise answer that shows a solid grasp of the topic.
2. A fun, practical home experiment (easy, safe, and inexpensive) that demonstrates the concept, something the user can show to friends to impress them.
3. Possible applications of the concept in real-life scenarios or in other fields.
Please format the response in markdown, with each (i repeat each) question starting with a level 3 heading. 
Here are the questions:
"""
    prompt_for_not_attempted = """
I took a test on {topic_name}, but some questions were skipped. Please provide for each (i repeat each) question:

1. The correct answer.
2. Common misconceptions or reasons why someone might skip or avoid this question.
3. Applications of the concept and why it's useful to understand or apply it in real-life scenarios.
Please format the response in markdown, with each (i repeat each) question starting with a level 3 heading. Here are the questions:
"""
    prompt_for_workflow_qs = """
My workflow was interviewed in {topic_name}. Here is the description for what i did: {topic_desc}
Please provide for each (i repeat each) question:
1. What i could have done better
2. What i did well
3. Was my logic flawed? if so what i need to learn to fix it 
4. Any other comments
Please format the response in markdown, with each (i repeat each) question starting with a level 3 heading. Here are the questions:"""
    # * queries
    Query_wrong_Questions = "Select question, user_answer from questions where test_id = %s and topic_id = %s and correctness = False "
    Query_correct_Questions = "Select question, user_answer from questions where test_id = %s and topic_id = %s and correctness = True "
    Query_not_attempted_Questions = "Select question, user_answer from questions where test_id = %s and topic_id = %s and correctness is null "
    Query_workflow_Questions = "Select question, user_answer from workflow_questions where test_id = %s and topic_id = %s "
    # connecting to database
    
    m_db = conn.connect(host = my_host, user = my_user, passwd = pswd, database = dbname)
    cursor = m_db.cursor()
    cursor.execute("select topic_name, topic_description from topics where topic_id = %s", (topic_id))
    topic_name = cursor.fetchone()
    cursor.execute(Query_wrong_Questions, (test_id, topic_id))
    wrong_qs = cursor.fetchall()
    cursor.execute(Query_correct_Questions, (test_id, topic_id))
    correct_qs = cursor.fetchall()
    cursor.execute(Query_not_attempted_Questions, (test_id, topic_id))
    not_attempted_qs = cursor.fetchall()
    cursor.execute(Query_workflow_Questions, (test_id, topic_id))
    workflow_qs = cursor.fetchall()
    cursor.execute("select easy_Questions,medium_Questions,difficult_Questions from Tests where test_id = %s and topic_id = %s", (test_id,topic_id))
    qs_num = cursor.fetchone()
    cursor.execute("select question_type,count(*) from questions where Test_id = %s and topic_id = %s and correctness = True group by question_type", (test_id,topic_id))
    corr_qs_by_type = cursor.fetchall()
    cursor.close()
    m_db.close()
    # formatting the answers
    dict_to_return = {
        "Questions Done wrong": "",
        "Questions Done right": "",
        "Questions not attempted": "",
        "Workflow Questions": ""
    }
    if len(wrong_qs) > 0:
        for i in range(len(wrong_qs)):
            wrong_qs[i] ="\n\n\n\nTHE_QUESTION: "  + wrong_qs[i][0] + "\nMY_ANSWER: " + wrong_qs[i][1]
        if int(len(wrong_qs)/5)>0:
            # split it into list 
            wrong_ans_li = [wrong_qs[i:i+5] for i in range(0, len(wrong_qs), 5)]
            prompt_for_wrong_answers_lis = []
            for i in range(len(wrong_ans_li)):
                qs_for_prompt = " ".join(wrong_ans_li[i])
                prompt_temp = prompt_for_wrong_answers.format(topic_name =topic_name[0]) + qs_for_prompt
                prompt_for_wrong_answers_lis.append(prompt_temp)
            dict_to_return["Questions Done wrong"] = prompt_for_wrong_answers_lis
        else:
            prompt_temp =prompt_for_wrong_answers.format(topic_name =topic_name[0]) + " ".join(wrong_qs)
            dict_to_return["Questions Done wrong"] = prompt_temp

    if len(correct_qs) > 0:
        for i in range(len(correct_qs)):
            correct_qs[i] ="\n\n\n\nTHE_QUESTION: "  + correct_qs[i][0] + "\nMY_ANSWER: " + correct_qs[i][1]
        if int(len(correct_qs)/5)>0:
            # split it into list
            correct_ans_li = [correct_qs[i:i+5] for i in range(0, len(correct_qs), 5)]
            prompt_for_correct_answers_lis = []
            for i in range(len(correct_ans_li)):
                qs_for_prompt = " ".join(correct_ans_li[i])
                prompt_temp = prompt_for_correct_answers.format(topic_name =topic_name[0]) + qs_for_prompt
                prompt_for_correct_answers_lis.append(prompt_temp)
            dict_to_return["Questions Done right"] = prompt_for_correct_answers_lis
        else:
            prompt_temp =prompt_for_correct_answers.format(topic_name =topic_name[0]) + " ".join(correct_qs)
            dict_to_return["Questions Done right"] = prompt_temp

    if len(not_attempted_qs) > 0:
        for i in range(len(not_attempted_qs)):
            not_attempted_qs[i] ="\n\n\n\nTHE_QUESTION: "  + not_attempted_qs[i][0] + "\nMY_ANSWER: " + not_attempted_qs[i][1]
        if int(len(not_attempted_qs)/5)>0:
            # split it into list    
            not_attempted_ans_li = [not_attempted_qs[i:i+5] for i in range(0, len(not_attempted_qs), 5)]
            prompt_for_not_attempted_answers_lis = []
            for i in range(len(not_attempted_ans_li)):
                qs_for_prompt = " ".join(not_attempted_ans_li[i])
                prompt_temp = prompt_for_not_attempted.format(topic_name =topic_name[0]) + qs_for_prompt
                prompt_for_not_attempted_answers_lis.append(prompt_temp)
            dict_to_return["Questions not attempted"] = prompt_for_not_attempted_answers_lis
        else:
            prompt_temp =prompt_for_not_attempted.format(topic_name =topic_name[0]) + " ".join(not_attempted_qs)
            dict_to_return["Questions not attempted"] = prompt_temp

    if len(workflow_qs) > 0:
        for i in range(len(workflow_qs)):
            workflow_qs[i] ="\n\n\n\nTHE_QUESTION: "  + workflow_qs[i][0] + "\nMY_ANSWER: " + workflow_qs[i][1]
        if int(len(workflow_qs)/5)>0:
            # split it into list
            workflow_ans_li = [workflow_qs[i:i+5] for i in range(0, len(workflow_qs), 5)]
            prompt_for_workflow_answers_lis = []
            for i in range(len(workflow_ans_li)):
                qs_for_prompt = " ".join(workflow_ans_li[i])
                prompt_temp = prompt_for_workflow_qs.format(topic_name =topic_name[0]) + qs_for_prompt
                prompt_for_workflow_answers_lis.append(prompt_temp)
            dict_to_return["Workflow Questions"] = prompt_for_workflow_answers_lis
        else:
            prompt_temp =prompt_for_workflow_qs.format(topic_name =topic_name[0]) + " ".join(workflow_qs)
            dict_to_return["Workflow Questions"] = prompt_temp
    max_score = int(qs_num[0]) + int(qs_num[1])*2 + int(qs_num[2])*3
    weightage = {"easy":1, "medium":2,"difficult":3}
    acc_score = sum(weightage[cat] *count for cat, count in corr_qs_by_type)
    dict_to_return["Over_all_score"] = (acc_score/max_score)*100
    dict_to_return["test_details"] = st.session_state.p_test_details
    return dict_to_return

def generate_mds_and_md_file(model_instance, returned_dict:dict):

    file_na = os.path.join(os.getcwd(),"Assets","Results", f"{returned_dict['p_test_details']['topic_name']}_test_{returned_dict['p_test_details']['test_id']}.md")
    with open(file_na, "w", encoding="utf-8") as f:
        f.write(f"# Practical Activity Evaluation of {returned_dict['p_test_details']['topic_name']}_test_{returned_dict['p_test_details']['test_id']}\n\n")
        f.write(f"## Overall Score : {returned_dict['Over_all_score']}\n\n")
    if type(returned_dict["Questions Done wrong"]) != list and returned_dict["Questions Done wrong"] != "":
        res = model_instance.generate_content(returned_dict["Questions Done wrong"])
        Done_wrong_section_str= res.text
    elif type(returned_dict["Questions Done wrong"]) == list:
        Done_wrong_section_str=""
        for i in range(len(returned_dict["Questions Done wrong"])):
            res = model_instance.generate_content(returned_dict["Questions Done wrong"][i])
            Done_wrong_section_str =  Done_wrong_section_str + res.text
    else:
        Done_wrong_section_str= "You did not attempt any question wrong! Well done! :astonished: \n\n"

    if type(returned_dict["Questions Done right"]) != list and returned_dict["Questions Done right"] != "":
        res = model_instance.generate_content(returned_dict["Questions Done right"])
        Done_correct_section_str= res.text
    elif type(returned_dict["Questions Done right"]) == list:
        Done_correct_section_str=""
        for i in range(len(returned_dict["Questions Done right"])):
            res = model_instance.generate_content(returned_dict["Questions Done right"][i])
            Done_correct_section_str =  Done_correct_section_str + res.text
    else:
        Done_correct_section_str= "You did not attempt any question right. Try harder next time. \n\n"

    if type(returned_dict["Questions not attempted"]) != list and returned_dict["Questions not attempted"] != "":
        res = model_instance.generate_content(returned_dict["Questions not attempted"])
        not_attempted_section_str= res.text
    elif type(returned_dict["Questions not attempted"]) == list:
        not_attempted_section_str=""
        for i in range(len(returned_dict["Questions not attempted"])):
            res = model_instance.generate_content(returned_dict["Questions not attempted"][i])
            not_attempted_section_str =  not_attempted_section_str + res.text
    else:
        not_attempted_section_str= "You attempted all Questions. Good job :slight_smile: \n\n"

    if type(returned_dict["Workflow Questions"]) != list and returned_dict["Workflow Questions"] != "":
        res = model_instance.generate_content(returned_dict["Workflow Questions"])
        workflow_section_str= res.text
    elif type(returned_dict["Workflow Questions"]) == list:
        workflow_section_str=""
        for i in range(len(returned_dict["Workflow Questions"])):
            res = model_instance.generate_content(returned_dict["Workflow Questions"][i])
            workflow_section_str =  workflow_section_str + res.text
    else:
        workflow_section_str= "No Questions answered"
    
    # w-flow: i made this section to better the workflow based on context i will provide
    impoved_workflow_prompt = """based on the below conversation and improvements provided a better way to do what i did step by step.
The Answer should be in markdown style starting with heading 3.
CONTEXT: \{CONVERSATION USED TO ASK FOR IMPROVEMENT SUGGESTIONS:
{Per_prompt}
\}
\{ANSWER I GOT:
{imp_ans}
 \}
""".format(Per_prompt = returned_dict["Workflow Questions"], imp_ans = workflow_section_str)
    res = model_instance.generate_content(impoved_workflow_prompt)
    better_my_wrokflow_section_str = res.text

    with open(file_na, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(f"## :white_check_mark: Questions Done right\n\n{Done_correct_section_str}\n\n")
        f.write(f"## :x: Questions Done wrong\n\n{Done_wrong_section_str}\n\n")
        f.write(f"## :question: Questions not attempted\n\n{not_attempted_section_str}\n\n")
        f.write(f"## :construction: Workflow\n\n{workflow_section_str}\n\n")
        f.write(f"## :bulb: Workflow Improvements\n\n{better_my_wrokflow_section_str}\n\n")
    
    with open(file_na, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    test_det_dict = returned_dict["test_details"]
    test_det_dict["score"] = returned_dict["Over_all_score"]
    return markdown_content, file_na, test_det_dict
generate_mds_and_md_file_partial = partial(generate_mds_and_md_file, model_instance = model)

@st.dialog("Evaluation Summary")
def evaluation_summary_dialog(md_str,file_name):
    st.markdown(md_str)
    st.download_button("Download evaluation report", data = md_str, file_name = file_name, mime = "text/markdown")

def callable_display_func(markdown_str, file_name, ts_dict):
    from math import ceil
    test_id = ts_dict["test_id"]
    topic_id = ts_dict["topic_id"]
    db = conn.connect(
        host = my_host,
        user = my_user,
        passwd = pswd,
        database = dbname
    )
    cur = db.cursor()
    cur.execute("UPDATE tests set score = %s, suggestion = %s where test_id = %s and topic_id = %s", (ceil(ts_dict["score"]), markdown_str, test_id, topic_id))
    db.commit()
    cur.close()
    db.close()
    evaluation_summary_dialog(markdown_str, file_name)
    if "p_disp_Qs" in st.session_state:
        del st.session_state.p_disp_Qs
    if "p_test_details" in st.session_state:
        del st.session_state.p_test_details

if "p_test_details" in st.session_state:
    eval_btn = st.button("Evaluate the Activity")
    if eval_btn:
        eval_res_dict = format_qs_and_workflow_ans(st.session_state.p_test_details["test_id"], st.session_state.p_test_details["topic_id"])
        res_md, res_md_name, ts_det_dict = generate_mds_and_md_file_partial(eval_res_dict)
        callable_display_func(res_md, res_md_name, ts_det_dict)