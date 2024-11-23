import google.generativeai as genai
import streamlit as st
import datetime as dt
import Consistancy_tables as su 
import os

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

def Redo_Assesment(): 
    delete_from_sessionstate()
def del_proj_attrib():
    if "projects" in st.session_state and len(st.session_state.projects) > 0:
        del st.session_state.projects
def delete_from_sessionstate():
    if "suggestions_project" in st.session_state:
        del st.session_state["suggestions_project"]
    if "Marks_project" in st.session_state:
        del st.session_state["Marks_project"]
    if "Questions_project" in st.session_state:
        del st.session_state["Questions_project"]
def eval_and_send():
    if "projects" in st.session_state and len(st.session_state.projects) > 0:
        if "suggestions_project" in st.session_state:
            if st.session_state.suggestions_project is not None and len(st.session_state.suggestions_project) > 0:
                my_suggestions = ". ".join(st.session_state.suggestions_project[0:])
                my_suggestions = "".join([s for s in my_suggestions.splitlines(True) if s.strip("\r\n")])
                my_suggestions = my_suggestions.replace('"'," ")
                my_suggestions = my_suggestions.replace("'"," ")
        if "Marks_project" in st.session_state:
            overall_marks = st.session_state.Marks_project
            if overall_marks <30:
                my_score = 0
            elif 30< overall_marks <89:
                my_score = 1
            else:
                my_score = 2
        if "projects" in st.session_state:
            generation_config = {
          "temperature": 0.9,
          "top_p": 0.95,
          "top_k": 64,
          "max_output_tokens": 8192,
          "response_mime_type": "text/plain",
        }
            model = genai.GenerativeModel(model_name="gemini-1.5-flash",generation_config=generation_config)
            prompt_gen_topic_heading = f"Describe in two line what i did in the project, basically give it a heading. Here are the details {st.session_state.projects} "
            my_topic = model.generate_content(prompt_gen_topic_heading).text

        if my_topic is not None and my_score is not None and my_suggestions is not None:
            Query = f"Insert into my_progress (The_topic,The_test_result, The_suggestion) values ('{my_topic}',{my_score}, '{str(my_suggestions)}')"
            db, cur =su.connnecting()
            try:
                cur.execute(Query)
                db.commit()
                st.success(f"Query executed {Query}")
            except Exception as e:
                st.error(e)
            finally:
                db.close()
    if "projects" in st.session_state and len(st.session_state.projects) > 0:
        del st.session_state["projects"]
    delete_from_sessionstate()
                
class My_EVAL_Project:
    Questions = []
    Answer_user = []

    def generate_Quetions(self, topic):
        # first Question will be easy
        generation_config = {
          "temperature": 0.9,
          "top_p": 0.95,
          "top_k": 64,
          "max_output_tokens": 8192,
          "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(model_name="gemini-1.5-flash",generation_config=generation_config)
        prompt_gen_all_questions_end_with_special_char = f"Generate 1 easy,2 medium and 2 difficult Questions to evaluate how well i understood what i did in project, what i did is {topic}, make sure that each Question can be answered within 100 words and you can test them later. All Questions must be dissimilar to cover diverse ranfe in the topic. separate each Question by characters- 'END1:STA2' only and no need to specify anything else. "
        character = "END1:STA2"
        res = model.generate_content(prompt_gen_all_questions_end_with_special_char)
        self.Questions = res.text.split(character)
        print(self.Questions)
        print("Questions generated successfully ", dt.datetime.now())
    
    def Evaluate_Answer_user_proj(self,specific_question,the_usr_answer, what_i_did_for_project):
        generation_config = {
          "temperature": 0.9,
          "top_p": 0.95,
          "top_k": 64,
          "max_output_tokens": 8192,
          "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(model_name="gemini-1.5-flash",generation_config=generation_config)
        prompt_to_evaluate = f"Evaluate my answer: {the_usr_answer} for the question: {specific_question}. Respond with only one word: 'correct' or 'incorrect.' Consider various answer formats (e.g., single words, phrases, sentences) and context. Be generous in your evaluation, marking it as 'incorrect' only if the factual or logical aspect is clearly wrong."
        res = model.generate_content(prompt_to_evaluate)
        my_eval = {
            "Correctedness": res.text
        }
        print(the_usr_answer, dt.datetime.now())
        print(specific_question, dt.datetime.now())
        if "incorrect" in my_eval["Correctedness"] or "Incorrect" in my_eval["Correctedness"]:
            correct_answer = model.generate_content(f"I did for project: {what_i_did_for_project} \n but gave an incorrect answer for the question: {specific_question}. My answer was {the_usr_answer}. What is the correct answer?")
            suggestions = model.generate_content(f"I did for project: {what_i_did_for_project}\n but gave an incorrect answer for the question: {specific_question}. My answer was {the_usr_answer}. What did i miss to get it wrong? What further improvements can be done to learn better?")
            my_eval["suggestions"] = suggestions.text
            my_eval["correct_answer"] = correct_answer.text
            print(my_eval, dt.datetime.now())
            return my_eval, 3
        elif "correct" in my_eval["Correctedness"] or "Correct" in my_eval["Correctedness"]:
            improvements = model.generate_content(f"My answer is correct,do you want to add something to it? My answer is: {the_usr_answer}, the question is: {specific_question}")
            my_eval["suggestions"] = improvements.text
            print(my_eval, dt.datetime.now())
            return my_eval, 2
        return my_eval,0
    def compress_suggestions(self):
        generation_config = {
          "temperature": 0.9,
          "top_p": 0.95,
          "top_k": 64,
          "max_output_tokens": 8192,
          "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(model_name="gemini-1.5-flash",generation_config=generation_config)
        if "Suggestions_project" in st.session_state and len(st.session_state.Suggestions_project) > 0:
            Prompt_to_compress_suggestions = f"I gave a short test to evaluate how well i understood what i did in project ({st.session_state.projects['description']}). The questions are: {self.Questions}, the suggestions i got based on my answers are compiled in this text: {st.session_state.Suggestions_project}.Please summarize what i should do in points."
            print(Prompt_to_compress_suggestions)
            res = model.generate_content(Prompt_to_compress_suggestions)
            st.session_state.Suggestions_project = res.text
            st.success("Suggestions compressed successfully")
        else:
            st.error("No suggestions to compress")
if "projects" in st.session_state and len(st.session_state.projects) > 0:
    if "Questions_project" not in st.session_state:
        this_instance_evaluation = My_EVAL_Project()
        this_instance_evaluation.generate_Quetions(st.session_state.projects['description'])
        st.session_state.Questions_project = this_instance_evaluation.Questions

    @st.fragment()
    def take_answers_proj():
        for i in range(len(st.session_state.Questions_project)):
            with st.form(f"form {i}"):
                st.write(st.session_state.Questions_project[i])
                answer = st.text_area("Your answer for "+ str(i))
                submit = st.form_submit_button("Check answer" +str(i))
                if submit:
                    eval, score = this_instance_evaluation.Evaluate_Answer_user_proj(st.session_state.Questions_project[i],answer, st.session_state.projects['description'])
                    st.write(eval)
                    # implement sending marks logic here
                    if "suggestions_project" not in st.session_state:
                        st.session_state.suggestions_project = []
                    if score == 2:
                        if "Marks_project" not in st.session_state:
                            st.session_state.Marks_project = 10
                        elif i==0:
                            st.session_state.Marks_project += 10
                        elif i== 1 or i== 2:
                            st.session_state.Marks_project += 20
                        elif i== 3 or i== 4:
                            st.session_state.Marks_project += 25
                        st.session_state.suggestions_project.append(eval["suggestions"])
                    if score == 3:
                        if "suggestions_project" not in st.session_state:
                            st.session_state.suggestions_project = []
                        st.session_state.suggestions_project.append(eval["suggestions"])
                        st.session_state.suggestions_project.append(eval["correct_answer"])
                    st.write(score)
    take_answers_proj()
    col1,col2,col3 = st.columns([1,3,1])
    col1.button("Submit evaluation", on_click=eval_and_send)
    col3.button("Clear evaluation",on_click= Redo_Assesment)
else:
    st.write("Go to main app and generate topic")
    st.page_link( "pages/Main_app.py",label="Go to main app",icon="🏠")