
import streamlit as st 
import os
import google.generativeai as genai

import Consistancy_tables_with_orm as su
from utilities import GoogleGenAIUtilities as gg
import mysql.connector as conn

import pandas as pd
import datetime as dt

# def get_mykey():
#     found = 0
#     dir_per =""
#     for dirpath, dirnames, filenames in os.walk(os.getcwd()):
#         if "api_key.txt" in filenames:
#             found = 1
#             dir_per = dirpath
#             break
#     if found == 1:
#         with open(os.path.join(dir_per, "api_key.txt")) as f:
#             api_k = f.readlines()
#         return api_k[0].replace("\n","")
#     else:
#         st.error("No api_key.txt found")
#         st.stop()
#         return None
g_creds = gg()
api_key_from_func = g_creds.api_key
if api_key_from_func is None:
    st.error("No api_key.txt found in the current directory.\n Please make sure that api_key.txt is present in the current directory (project root )")
    st.stop()
else:
    genai.configure(api_key=api_key_from_func)
# my_host, my_user, my_password, my_db_name = su.getconnnames()
# #fetch the data and then ask for suggestions
# # 1 fetch the data
# My_db, My_cur = su.connnecting()
# Query = "SELECT * FROM struggles where The_date >= date_sub(curdate(),interval 20 day)"

# My_cur.execute(Query)
# data = My_cur.fetchall()
# st.data_editor(data, use_container_width=True)

def Get_next_steps():
    """Baiscally it will help me get the suggestions via chat imporvements"""
    try:
        m_db, m_cur = su.connecting_connector()
        # getting struggles
        twenty_days_ago = dt.date.today() - dt.timedelta(days=20)
        m_cur.execute("""
        SELECT * FROM struggles
        WHERE The_date >= %s and user_id = %s
    """, (twenty_days_ago,st.session_state.authenticated_user.user_id))
        data = m_cur.fetchall()
    except Exception as e:
        st.error(f"Query not executed {e}")
        data = "Sorry no data found, provide general suggestions"
        st.stop()
    finally:
        m_cur.close()
        m_db.close()

    prompt_next_steps = f"""These are some struggles that i had during the past 20 days. 
    Analyse this data and convert it into some actionable steps that i can take to improve. 
    {data}"""
    gen_conf = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 20,
        "max_output_tokens": 8192,
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=gen_conf)
    res = model.generate_content(prompt_next_steps)
    return res.text

def Give_data():
    """Baiscally it will help me get the suggestions via tests table"""

    try:
        twenty_days_ago = dt.date.today() - dt.timedelta(days=20)
        My_db, My_cur = su.connecting_connector()
        My_cur.execute("SELECT suggestions FROM tests where test_date >= The_date >= %s and user_id = %s", (twenty_days_ago,st.session_state.authenticated_user.user_id))
        prog = My_cur.fetchall()
    except Exception as e:
        st.error(f"Query not executed {e}")
        prog = "Sorry no data found, provide general suggestions"
        st.stop()
    finally:
        My_cur.close()
        My_db.close()

    prompt_next_steps = f"""These suggestions were Given to me for some tests i took not necessarly on the same topic.
      Analyse this data and convert it into some actionable steps that i can take to improve. 
      {prog}"""
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 20,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    res = model.generate_content(prompt_next_steps)
    return res.text
def get_ideas():
    """Gets data from tests table test id test_date, 
    gets topic_id, topic_name form topics table"""
    try:
        db, cur = su.connecting_connector()
        Query_topics_i_did = "select topics.topic_id, topics.topic_name, topics.topic_description, avg(tests.score), group_concat(tests.suggestions,' \n\n\n\n ') as suggestions from tests left join topics on tests.topic_id = topics. topic_id group by topic_id where user_id = %s"
        cur.execute(Query_topics_i_did, (st.session_state.authenticated_user.user_id,))
        tp_i_did = cur.fetchall()
    except Exception as e:
        st.error(f"Query not executed {e}")
        tp_i_did = "Sorry no data found, provide general suggestions"
        st.stop()
    finally:
        cur.close()
        db.close()

    prompt_My_progress_suggestions = f"""I have done some tests on topics and i have got some suggestions for the same. Analyse this data and convert it into some actionable steps. Guide me in the right direction for what i am doing. {tp_i_did}"""
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 20,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    res = model.generate_content(prompt_My_progress_suggestions)
    return res.text
def stream_write(text):
    for i in text.split(" "):
        yield i + " "
col1,col2, col3 = st.columns([1,3,1])
sug = col1.button("Get Suggestions for improvement")
idea_but = col2.button("Get Path for next steps")
strug = col3.button("Get Advice")
if sug:
    text = Give_data()
    st.write_stream(stream_write(text))
if strug:
    text = Get_next_steps()
    st.write_stream(stream_write(text))
if idea_but:
    text = get_ideas()
    st.write_stream(stream_write(text))


# st.write(data)

# w-flow finally starting to create a summary

# // import matplotlib.pyplot as plt

# seg-expl: get topics for analysis

my_db, my_cur = su.connecting_connector()

# seg-expl taking all tables for analysis

my_cur.execute("select * from topics where user_id = %s", (st.session_state.authenticated_user.user_id,))
topics_table = my_cur.fetchall()
# my_cur.execute("show columns from topics where user_id = %", (st.session_state.authenticated_user.user_id,))
my_cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'topics'
      AND table_schema = 'public'
    ORDER BY ordinal_position;
""")
topics_columns = my_cur.fetchall()
my_cur.execute("select * from questions where user_id = %s", (st.session_state.authenticated_user.user_id,))
Questions_table = my_cur.fetchall()
my_cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'questions'
      AND table_schema = 'public'
    ORDER BY ordinal_position;
""")
Questions_columns = my_cur.fetchall()
my_cur.execute("select * from my_progress where user_id = %s", (st.session_state.authenticated_user.user_id,))
my_progress_table = my_cur.fetchall()
# my_cur.execute("show columns from my_progress")
my_cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'my_progress'
      AND table_schema = 'public'
    ORDER BY ordinal_position;
""")
my_progress_columns = my_cur.fetchall()
my_cur.execute("Select * from tests where user_id = %s", (st.session_state.authenticated_user.user_id,))
tests_table = my_cur.fetchall()
# my_cur.execute("show columns from tests")
my_cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'tests'
      AND table_schema = 'public'
    ORDER BY ordinal_position;
""")
tests_columns = my_cur.fetchall()
my_db.commit()
my_cur.close()
my_db.close()



# w-flow i will show how many tests were taken for the specific topic
# w-flow comapre scores of each tests for topics with same topic type  
# w-flow compare no of easy hard and medium Questions for each topic test 
# w-flow frequency of tests

#seg-expl No of tests taken by time
def create_dfs(table, columns):
    col_df = pd.DataFrame(columns)
    columns = col_df[:][0]
    tab_df = pd.DataFrame(table, columns=columns)
    return tab_df.copy()

test_df = create_dfs(tests_table, tests_columns)
test_df["test_date"] = test_df["test_date"].dt.date

# // st.write(test_df["test_date"].value_counts())
st.markdown("### Number of Tests Taken by Date")
st.bar_chart(test_df["test_date"].value_counts().sort_values( ascending = False), x_label="Date", y_label="Number of tests")
# // plt.xlabel("Date")
# // plt.ylabel("Number of Tests")
# // "Number of Tests Taken by Date"
# // plt.xticks(rotation=45)
# // plt.tight_layout()
# // plt.show()

# seg-expl: i am creating no of topics added/learnt by date grouped by topic type 

topics_df = create_dfs(topics_table, topics_columns)
topics_df["topic_start_date"] = topics_df["topic_start_date"].dt.date

# seg-expl create data by date like date, skill learnt,implementations done 

cat_counts = topics_df.groupby(['topic_start_date', 'topic_type']).size().unstack(fill_value=0)
print(cat_counts)
# ? used unstack
st.markdown("### Number of topics added by Date")
st.bar_chart(cat_counts, use_container_width=True,x_label="Date", y_label="Number of Topics")

# w-flow create test_id specific easy medium and difficult Questions
cat_counts_tst = test_df.drop(["test_date", "topic_id", "score", "suggestions"], axis=1)
st.markdown("### Number of Questions in each test")
st.bar_chart(cat_counts_tst, x="test_id", y=["easy_questions", "medium_questions", "difficult_questions"], use_container_width=True, x_label="Test ID", y_label="Number of Questions",color=["#FF0000", "#0000FF", "#00FF00"])
# w-flow test_id by test score line chart
test_id_by_test_score_df = test_df[["test_id", "score"]]
st.markdown("### Number of Tests Taken by score")
st.line_chart(test_id_by_test_score_df, x="test_id", y="score", use_container_width=True, x_label="Test ID", y_label="Score")
# w-flow select topic and based on that we will give you the information

# seg-expl creating a function taht will for all tests in a topic return
# seg-expl correct Questions, not attempted Question, wrong_questions
qs_df = create_dfs(Questions_table, Questions_columns)
def gen_charts(topic_id):
    for id in test_df[test_df['topic_id'] == topic_id]['test_id']:
    
        st.markdown("### Test "+str(id)+" Questions")
        qs = qs_df[qs_df['test_id'] == id][['question_type','correctness']]
        qs["correctness"]= qs["correctness"].fillna(0)
        dat =qs.groupby(['question_type', 'correctness']).size().unstack(fill_value=0)
        
        st.bar_chart(dat, use_container_width=True,x_label="Question Type for test "+str(id), y_label="correctiness number")
        # except:
        #     st.error("No questions found for test "+str(id))

with st.form("Topic to fetch"):
    dd = topics_df.loc[:,["topic_id","topic_name"]].to_dict()
    ddl= []
    # dd[key1][ind1],dd[key2][ind1]
    keys = list(dd.keys())
    for i in range(len(dd[keys[0]])):
        tup =[]
        for k in keys:
            tup.append(dd[k][i])
        ddl.append(tuple(tup))

    topic_id = st.selectbox("Select Topic",(ddl))
    print(topic_id)
    submit_button = st.form_submit_button("Submit")
    if submit_button:
            gen_charts(topic_id[0])


# dat = pd.DataFrame(topics_df["topic_start_date"].groupby(topics_df["topic_type"]).value_counts())
# dat_df = dat.reset_index(inplace=False)
# st.write(dat_df)
# st.line_chart(dat_df, x = "topic_start_date", use_container_width=True,color="topic_type")
# st.line_chart(topics_df["topic_start_date"].groupby(topics_df["topic_type"]).value_counts().sort_values( ascending = False), x = "topic_start_date",y=["count", "topic_type"], use_container_width=True,color=["#FF0000", "#0000FF"])

# st.write(dat_df)