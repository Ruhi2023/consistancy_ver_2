
import streamlit as st 

import google.generativeai  as genai
import Consistancy_tables as su
from functools import partial
import datetime as dt
import os
import math
# initialization
#// st.session_state
api_key_from_func = su.get_mykey()
genai.configure(api_key=api_key_from_func)
# configure genai for model
model_conf = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 20,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=model_conf)
my_host, my_user, my_passwd, dbname = su.getconnnames()

#  tasks
# 1. generate form for test 
#     (UI ) 1. create form for fornt end 
#     (DB ) 2. store in database for backend
#     (st_session state) 3. return dict of test_id, topic_id, easy_qs, medium_qs, difficult_qs
# 2. get Questions
        # (st_session state) 1. call the function to generate the Questions
        # (separate function to call) 2. generate Questions and put in databse
        # (format data as python dict/tup) 3. get Questions from database 
        # (UI) 4. display Questions in the form of a form
        # (pyfunc) 5. get answers from user and store in database along with correctness (use question id other ids)
        # 6. evaluate each answer's correctness 
# 3. get evaluation and store in databse
        # 1. Generate results form user answers
        # 2. store in a markdown file
        # 3. store in database and display as a dialog + get st.sessionstate.display_questions deleted

if 'rerun_counter' not in st.session_state:
    st.session_state.rerun_counter = 0

st.session_state.rerun_counter += 1

# seg-expl removing the formsubmitter with last id = anything but reruncounter
# ! dangerous
for key in st.session_state:
    if key.startswith("FormSubmitter") and not key.endswith(str(st.session_state.rerun_counter)) and key != "FormSubmitter:test creting form-Test what i learnt" :
        del st.session_state[key]

# 1. generate form for test 
#     (DB ) 2. store in database for backend
def store_test_in_db(eno, mno, hno, topic_id, tp_name):
    # check if the test is requirement friendly ie more than 4 questions
    if (eno+mno+hno) <= 4:
        st.warning("Please select atleast 5 questions from any difficulty level")
        return 0
    else:
        the_db, the_cur = su.connnecting(
            host = my_host,
            user = my_user,
            passwd = my_passwd,
            database = dbname
        )
        the_cur.execute("Insert into Tests (easy_Questions,medium_Questions,difficult_Questions,topic_id) values (%s,%s,%s,%s)",(int(eno),int(mno),int(hno),topic_id))
        test_id_val = the_cur.lastrowid
        the_db.commit()
        the_cur.close()
        the_db.close()
        r_di = {"test_id":test_id_val,"topic_id":topic_id,"eno":eno,"mno":mno,"hno":hno, "topic_name":tp_name}
        return r_di
#     (UI ) 1. create form for fornt end 
with st.form("test creting form"):
    db, cur = su.connnecting(
        host = my_host,
        user = my_user,
        passwd = my_passwd,
        database = dbname
    )
    cur.execute("Select topic_id, topic_name from Topics where topic_type = 'skills'")
    topics_names = cur.fetchall()
    if len(topics_names) == 0:
        st.warning("No topics added yet")
        topics_names = [""]
    topic = st.selectbox("Select Topic",topics_names) 
    hard_num = st.number_input("Number of Hard Questions",min_value=0,max_value=10,value=5)
    mid_num = st.number_input("Number of Medium Questions",min_value=0,max_value=10,value=5)
    easy_num = st.number_input("Number of Easy Questions",min_value=0,max_value=10,value=5)
    if sum([easy_num,mid_num,hard_num]) <= 4:
        st.warning("Please select atleast 5 questions from any difficulty level")
    db.commit()
    cur.close()
    db.close()
    submit_button = st.form_submit_button("Test what i learnt")
    if submit_button:
#     (st_session state) 3. return dict of test_id, topic_id, easy_qs, medium_qs, difficult_qs
        st.session_state.test_details = store_test_in_db(eno=easy_num, mno=mid_num, hno=hard_num, topic_id=topic[0], tp_name=topic[1])
        st.session_state.generate_questions = True
        
# 2. get Questions
# (separate function to call) 2. generate Questions and put in databse
def Questions_already_in_db_fetch_for_prompt(test_id, topic_id,level):
    db,cur = su.connnecting()
    Query = "Select Question from Questions where Test_id = %s and Topic_id = %s and Question_type = %s"
    cur.execute(Query, (test_id, topic_id, level))
    Ques_db_unformatted = cur.fetchall()
    db.commit()
    cur.close()
    db.close()
    if len(Ques_db_unformatted) == 0:
        return "None yet"
    else:
        ste= "Question {que_no}:"
        ques_db =[]
        no= 1
        for Q in Ques_db_unformatted:
            ue = ste.format(que_no=no)
            ques_db.append(ue+Q[0])
            no+=1
        return "\n".join(ques_db)


def generate_questions_and_put_in_db(Test_id, topic_id, level, model, question_no):
    # generate question according to level
    topic_name = st.session_state.test_details["topic_name"]
    Easy_Question_prompt = """Generate a very short answer type Question from the topic- {}. 
    The question must be unique and easy for someone learning the topic to answer.Output only the question with no additional text or explanation. 
    Avoid duplication with the already generated Questions. 
    Questions alreay present are: {}""".format(topic_name, Questions_already_in_db_fetch_for_prompt(test_id=Test_id, topic_id=topic_id, level="easy"))
    medium_Question_Prompt = """Generate a unique, short-answer question for the topic- '{}'. 
    The question should focus on testing deep understanding of the topic and should be either easy or moderately difficult for someone learning the topic. 
    Output only the question with no additional text or explanation. 
    Avoid duplication with the following already generated questions: {}""".format(topic_name, Questions_already_in_db_fetch_for_prompt(test_id=Test_id, topic_id=topic_id, level="medium"))
    hard_Question_prompt = """Generate a unique, hard question from the topic '{}'. 
    The question should test advanced understanding but require a brief, concise answer (no more than 1-2 sentences). 
    Avoid verbose questions, and avoid duplication with the following already generated questions: {}. 
    Only output the question, without any extra text.""".format(topic_name, Questions_already_in_db_fetch_for_prompt(test_id=Test_id, topic_id=topic_id, level="difficult"))
    if level == "easy":
        myprompt = Easy_Question_prompt
    elif level == "medium":
        myprompt = medium_Question_Prompt
    else:
        myprompt = hard_Question_prompt
    print(myprompt)
    # // response = model.generate(prompt=myprompt, max_tokens=200, temperature=0.9, top_p=1, top_k=64, stop="NEXT_QUESTION")
    res = model.generate_content(myprompt)
    my_db,my_cur = su.connnecting(
        host = my_host,
            user = my_user,
            passwd = my_passwd,
            database = dbname
    )
    my_cur.execute("INSERT INTO Questions (Test_id, Topic_id, Question_no, Question_type, Question) VALUES (%s, %s, %s, %s, %s)", (Test_id, topic_id, question_no,level, res.text))
    my_db.commit()
    # Done: inserted the Questions in db
    
# (format data as python dict/tup) 3. get Questions from database 
def fetch_format_questions_from_db(ts_id, tp_id):
    """returns a dict that will have all the questions formatted for form generation
    structure of dict= {Question_no: int,
                        Question: str,
                        Answer: str (it's from user)}"""
    # Done: think how to handel evaluation
    my_lis = []
    my_db, my_cur = su.connnecting(
        host = my_host,
            user = my_user,
            passwd = my_passwd,
            database = dbname
    )
    
    my_cur.execute("Select question_no, question, question_type from Questions where Test_id = %s and topic_id = %s", (ts_id,tp_id))
    my_l = my_cur.fetchall()
    my_db.commit()
    my_cur.close()
    my_db.close()
    for i in my_l:
        dict_ = {"Question_no":i[0],"Question":i[1],"Question_type":i[2]}
        my_lis.append(dict_)
    st.session_state.display_Questions = True
    return my_lis
# (pyfunc) 5. get answers from user and store in database along with correctness (use question id other ids)
def evaluate_and_store_answers(d_of_qs_with_ans: dict, model_instance):
    """evaluates the answer and stores it in database but it also needs a model instance"""
    prompt_check_Question = """Evaluate the answer and just say 1 word correct or incorrect. 
    Remember that the answer has been given in a limited space and is probabilly a summary. 
    The Question: {Question_no}. The answer: {user_answer}""".format(Question_no = d_of_qs_with_ans["Question"], user_answer = d_of_qs_with_ans["user_Answer"])
    prompt_correct_answer_form_model = """The Question: {} \nMy answer: {} \n What did i miss for this answer is incorrect?""".format(d_of_qs_with_ans["Question"], d_of_qs_with_ans["user_Answer"])
    res = model_instance.generate_content(prompt_check_Question)
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
    # // st.success("Your score is: " + str(score))
    # * store answer in database
    if score > 0:
        my_db_of_qs, my_cur_of_qs = su.connnecting(
            host = my_host,
            user = my_user,
            passwd = my_passwd,
            database = dbname)
        if score == 1:
            answer_correct_bool = True
        if score == 2:
            answer_correct_bool = False
        try:
            my_cur_of_qs.execute("Update Questions set user_answer = %s , correctness= %s where question_no = %s and topic_id = %s and test_id = %s", (d_of_qs_with_ans["user_Answer"], answer_correct_bool, d_of_qs_with_ans["Question_no"], st.session_state.test_details["topic_id"], st.session_state.test_details["test_id"]))
        except:
            st.error("Question not found in the database")
        finally:
            my_db_of_qs.commit()
            my_cur_of_qs.close()
            my_db_of_qs.close()
        

evaluate_and_store_answers_partial = partial(evaluate_and_store_answers, model_instance=model)
generate_questions_and_put_in_db_partial = partial(generate_questions_and_put_in_db, model=model)

# seg-expl adding form counter to handel reruns


# (UI func) 4. display Questions in the form of a form
@st.fragment
def display_questions_in_form(d_of_qs: dict, rrc: int):
    form_title = f"{d_of_qs['Question_type']} Question {d_of_qs['Question_no']}_{rrc}"
    with st.form(form_title):
        st.markdown("### Level: "+ d_of_qs['Question_type'])
        st.write(d_of_qs['Question'])
        user_answer =st.text_area("Answer", key = f"ans_{form_title}")
        sbut = st.form_submit_button(f"Submit {form_title}")
        if sbut:
            # ill just return answer and Question no by a function_call
            d_of_qs['user_Answer'] = user_answer
            evaluate_and_store_answers_partial(d_of_qs)

# ill typecheck for questions
if "test_details" in st.session_state :
    if st.session_state.test_details == 0:
        st.warning("Please select atleast 5 questions from any difficulty level")
    if type(st.session_state.test_details) == dict and "generate_questions" in st.session_state :
        # (st_session state) 1. call the function to generate the Questions
        total_num_of_questions = st.session_state.test_details["eno"] + st.session_state.test_details["mno"] + st.session_state.test_details["hno"]
        #ill handel progress bar here
        prog = st.progress(0, text="Generating Questions")
        progval = 0       
        for i in range(total_num_of_questions):
            if i <= (st.session_state.test_details["eno"] -1) :
                level = "easy"
            elif i <= (st.session_state.test_details["eno"] + st.session_state.test_details["mno"] -1):
                level = "medium"
            else:
                level = "difficult"
            
            generate_questions_and_put_in_db_partial(Test_id=st.session_state.test_details["test_id"], topic_id=st.session_state.test_details["topic_id"], level=level, question_no=i+1)
            progval = int(progval + 100/total_num_of_questions)
            prog.progress(progval, text="Generating Questions")
        st.success(" ALL Questions generated successfully")
        del st.session_state.generate_questions
# fist ill take the dictionary
# ! error prone segment 
    Questions_for_form = fetch_format_questions_from_db(ts_id=st.session_state.test_details["test_id"], tp_id=st.session_state.test_details["topic_id"])
    if "display_Questions" in st.session_state:
        for i in range(len(Questions_for_form)):
            display_questions_in_form(Questions_for_form[i], st.session_state.rerun_counter)
            # // st.session_state.form_counter += 1


#  // st.session_state       
        
        

            
# 3. get evaluation and store in databse
    # 1. Get user answers form user answers
def format_user_answers(test_id, topic_id):
    """
    retruns the answers as sorted by 
    1. what the user did wrong
    2. what the user did right
    3. what the user did not attempt
    also returns the score of user"""
    # * prompts
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
# w-flow: now i want to get Questions for this prompt and calculate the score of user
# if any section ahs empty Questions then i want to handle it here as welll
    # Queries 
    Query_wrong_Questions = """Select question, user_answer from Questions where Test_id = %s and topic_id = %s and correctness = False"""
    Query_correct_Questions = """Select question, user_answer from Questions where Test_id = %s and topic_id = %s and correctness = True"""
    Query_not_attempted_Questions = """Select question, user_answer from Questions where Test_id = %s and topic_id = %s and correctness is null"""
    # connecting to database
    
    my_db, my_cur = su.connnecting(
        host = my_host,
            user = my_user,
            passwd = my_passwd,
            database = dbname
    )
    my_cur.execute(Query_wrong_Questions, (test_id, topic_id))
    wrong_questions = my_cur.fetchall()
    my_cur.execute(Query_correct_Questions, (test_id, topic_id))
    correct_questions = my_cur.fetchall()
    my_cur.execute(Query_not_attempted_Questions, (test_id, topic_id))
    not_attempted_questions = my_cur.fetchall()
    my_cur.execute("select topic_name from Topics where topic_id = %s", (topic_id,))
    topic_name = my_cur.fetchone()
    my_cur.execute("select question_type,count(*) from Questions where Test_id = %s and topic_id = %s and correctness = True group by question_type", (test_id, topic_id))
    correct_questions_by_type = my_cur.fetchall()
    my_cur.execute("select easy_Questions,medium_Questions,difficult_Questions from Tests where test_id = %s and topic_id = %s", (test_id,topic_id))
    total_questions = my_cur.fetchone()
    my_db.commit()
    my_cur.close()
    my_db.close()
    # now i can format them
    # * dict below will contain keys "Questions Done wrong", "Questions Done right", "Questions not attempted", "Over_all_score"
    dict_to_return = {"Questions Done wrong":"",
                      "Questions Done right":"",
                      "Questions not attempted":""}
    # formatting wrong questions
    if len(wrong_questions) > 0:
        # convert to acceptable string 
        for i in range(len(wrong_questions)):
            wrong_questions[i] = "\n\n\n\n THE_QUESTION:" +str(wrong_questions[i][0]) + "\n MY_ANSWER:" + str(wrong_questions[i][1])         
        if int(len(wrong_questions)/ 5) > 0:
            # we will split
    #         def split_list(input_list, chunk_size):
    # return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]
            wrong_answers_list_in_list = [wrong_questions[i:i + 5] for i in range(0, len(wrong_questions), 5)]
            # need to make as many prompts list
            prompt_for_wrong_answers_list = []
            for i in range(len(wrong_answers_list_in_list)):
                qs_for_prompt = " ".join(wrong_answers_list_in_list[i])
                prompt = prompt_for_wrong_answers.format(topic_name=topic_name[0]) + qs_for_prompt
                prompt_for_wrong_answers_list.append(prompt)
            dict_to_return["Questions Done wrong"] = prompt_for_wrong_answers_list
        else:
            prompt = prompt_for_wrong_answers.format(topic_name=topic_name[0]) + " ".join(wrong_questions)
            dict_to_return["Questions Done wrong"] = prompt
    # formatting correct questions
    if len(correct_questions) > 0:
        for i in range(len(correct_questions)):
            correct_questions[i] = "\n\n\n\n THE_QUESTION:" +str(correct_questions[i][0]) + "\n MY_ANSWER:" + str(correct_questions[i][1])         
        if int(len(correct_questions)/ 5) > 0:
            correct_answers_list_in_list = [correct_questions[i:i + 5] for i in range(0, len(correct_questions), 5)]
            prompt_for_correct_answers_list = []
            for i in range(len(correct_answers_list_in_list)):
                qs_for_prompt = " ".join(correct_answers_list_in_list[i])
                prompt = prompt_for_correct_answers.format(topic_name=topic_name[0]) + qs_for_prompt
                prompt_for_correct_answers_list.append(prompt)
            dict_to_return["Questions Done right"] = prompt_for_correct_answers_list
            # ! handeled by type checking
        else:
            prompt = prompt_for_correct_answers.format(topic_name=topic_name[0]) + " ".join(correct_questions)
            dict_to_return["Questions Done right"] = prompt
    # formatting not attempted questions
    if len(not_attempted_questions) > 0:
        for i in range(len(not_attempted_questions)):
            not_attempted_questions[i] = "\n\n\n\n THE_QUESTION:" +str(not_attempted_questions[i][0]) + "\n MY_ANSWER:" + str(not_attempted_questions[i][1])         
        if int(len(not_attempted_questions)/ 5) > 0:
            not_attempted_answers_list_in_list = [not_attempted_questions[i:i + 5] for i in range(0, len(not_attempted_questions), 5)]
            prompt_for_not_attempted_list = []
            for i in range(len(not_attempted_answers_list_in_list)):
                qs_for_prompt = " ".join(not_attempted_answers_list_in_list[i])
                prompt = prompt_for_not_attempted.format(topic_name=topic_name[0]) + qs_for_prompt
                prompt_for_not_attempted_list.append(prompt)
            dict_to_return["Questions not attempted"] = prompt_for_not_attempted_list
        else:
            prompt = prompt_for_not_attempted.format(topic_name=topic_name[0]) + " ".join(not_attempted_questions)
            dict_to_return["Questions not attempted"] = prompt
    # now let's score 
    max_score = int(total_questions[0]) + int(total_questions[1])*2 + int(total_questions[2]*3)
    weightage = {'easy': 1, 'medium': 2, 'difficult': 3}
    accquired_score = sum(weightage[category] * count for category, count in correct_questions_by_type)
    dict_to_return["Over_all_score"] = (accquired_score/max_score)*100
    dict_to_return["test_details"] = st.session_state.test_details
    return dict_to_return
    
# // st.session_state
# 2. store in a markdown file
def store_in_markdown_file(model_instance,res_in_db_dict:dict):

    # it will return a markdown file's text as a string and the name of the file i.e it's path 
    # w-flow: make heading in markdown file and then write the Questions and suhhestions in markdown file
    # // ! had error 
    # Done resolved by handeling key = ""
    
    print(res_in_db_dict)

    file_name = os.path.join(os.getcwd(),"Assets","Results", f"{res_in_db_dict['test_details']['topic_name']}_test_{res_in_db_dict['test_details']['test_id']}.md")
    
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"# Test Evaluation of {res_in_db_dict['test_details']['topic_name']}_test_{res_in_db_dict['test_details']['test_id']}\n")
        f.write("\n\n")
        f.write(f"## Over_all_score: {res_in_db_dict['Over_all_score']}%\n")
        f.write("\n\n")
    # now lets generate the Content to be written in the markdown file
    if type(res_in_db_dict["Questions Done right"]) != list and res_in_db_dict["Questions Done right"] != "":
        res =model_instance.generate_content(res_in_db_dict["Questions Done right"])
        Done_correct_section_str= res.text
    elif type(res_in_db_dict["Questions Done right"]) == list:
        Done_correct_section_str=""
        for i in range(len(res_in_db_dict["Questions Done right"])):
            res =model_instance.generate_content(res_in_db_dict["Questions Done right"][i])
            Done_correct_section_str = res.text + Done_correct_section_str
    else:
        Done_correct_section_str= "You did not attempt any question correctly. Try harder next time.\n\n"
    if type(res_in_db_dict["Questions not attempted"]) != list and res_in_db_dict["Questions not attempted"] != "":
        res =model_instance.generate_content(res_in_db_dict["Questions not attempted"])
        not_attempted_section_str= res.text
    elif type(res_in_db_dict["Questions not attempted"]) == list:
        not_attempted_section_str=""
        for i in range(len(res_in_db_dict["Questions not attempted"])):
            res =model_instance.generate_content(res_in_db_dict["Questions not attempted"][i])
            not_attempted_section_str = res.text + not_attempted_section_str
    else:
        not_attempted_section_str= "You did attempted all questions. Good job. :handshake:"
    if type(res_in_db_dict["Questions Done wrong"]) != list and res_in_db_dict["Questions Done wrong"] != "":
        res =model_instance.generate_content(res_in_db_dict["Questions Done wrong"])
        Done_wrong_section_str= res.text
    elif type(res_in_db_dict["Questions Done wrong"]) == list:
        Done_wrong_section_str=""
        for i in range(len(res_in_db_dict["Questions Done wrong"])):
            res =model_instance.generate_content(res_in_db_dict["Questions Done wrong"][i])
            Done_wrong_section_str = res.text + Done_wrong_section_str
    else:
        Done_wrong_section_str= "Amazing! You did not attempt any question wrong. :astonished: \n\n"
    with open(file_name, "a", encoding="utf-8") as f:
        f.write("## Done_Correctly\n")
        f.write(Done_correct_section_str)
        f.write("\n\n")
        f.write("## Done_Wrongly\n")
        f.write(Done_wrong_section_str)
        f.write("\n\n")
        f.write("## Not_Attempted\n")
        f.write(not_attempted_section_str)
    with open(file_name, "r", encoding="utf-8") as f:
        markdown_string = f.read()
    ts_det_dict = res_in_db_dict["test_details"]
    ts_det_dict["score"] = res_in_db_dict["Over_all_score"]
    return markdown_string,file_name, ts_det_dict

    
store_in_markdown_file_partial = partial(store_in_markdown_file, model_instance= model)
# 3. store in database and  + get st.sessionstate.display_questions deleted
@st.dialog("Your evaluations")
def display_evaluations_display_only(markdown_string,md_name):
    st.markdown(markdown_string)
    st.download_button(label="Download Markdown", data=markdown_string, file_name=md_name, mime="text/markdown")
    
# ! display as a dialog to the function below gave error as module is not a callable object
# ? ill make a new function that just displays the markdown string and call it inside the function below
def display_evaluations(markdown_string,md_name, ts_det):
    test_id = ts_det["test_id"]
    topic_id = ts_det["topic_id"]
    # ! res_db = su.connnectingion(
    #     host = "localhost",
    #     user = "Ruhi",
    #     passwd = "Ruhi@5084",
    #     database = "consistancy"
    # )
    # done above was the actual error()
    res_db, cur = su.connnecting(
        host = my_host,
            user = my_user,
            passwd = my_passwd,
            database = dbname)
    
    cur.execute("update tests set score = %s, suggestions = %s where test_id = %s and topic_id = %s", (math.ceil(ts_det["score"]),markdown_string, test_id, topic_id))
    res_db.commit()
    cur.close()
    res_db.close()
    display_evaluations_display_only(markdown_string,md_name)
    if "display_questions" in st.session_state:
        del st.session_state.display_questions
    del st.session_state.test_details
    
# actually call all these
if "test_details" in st.session_state:
    evaluate_button = st.button("Evaluate my test")
    if evaluate_button:
        evaluated_results_dict = format_user_answers(test_id=st.session_state.test_details["test_id"],topic_id=st.session_state.test_details["topic_id"])
        myres_md,res_md_name, ts_det_dict = store_in_markdown_file_partial(res_in_db_dict=evaluated_results_dict)
        display_evaluations(myres_md,res_md_name, ts_det_dict)
        
