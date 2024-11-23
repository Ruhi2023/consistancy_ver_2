import streamlit as st 
import os
import google.generativeai as genai
import Consistancy_tables as su

# get_api_key_path = "./api_key.txt"
# with open(get_api_key_path) as f:
#     api_k = f.readlines()
# print(api_k)
# print(len(api_k[0]))
# newk = api_k[0].replace("\n","")
# print(len(newk))
# par = os.getcwd()
# print(par)
# dirname = os.path.dirname(par)
# print(dirname)
# oopath = os.path.abspath(os.path.join(par,".."))
# print(oopath)
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
#fetch the data and then ask for suggestions
# 1 fetch the data
My_db, My_cur = su.connnecting()
Query = "SELECT * FROM struggles where The_date >= date_sub(curdate(),interval 20 day)"

My_cur.execute(Query)
data = My_cur.fetchall()
st.data_editor(data, use_container_width=True)

def Get_inp_sug():
    """this will get me the suggestions from suggestions table"""
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    prompt = f"""Here are the suggestions i have been given for the past 20 days, it's going to be a long list. 
    Summarize it and convert it into some actionable steps. ***Suggestions start*** {data} ***suggestions end***"""
    res = model.generate_content(prompt)
    return res.text
def Get_Motivation():
    """Baiscally it will help me get the suggestions via progress table"""
    My_cur.execute("SELECT * FROM my_progress where Today >= date_sub(curdate(),interval 20 day)")
    prog = My_cur.fetchall()
    query = f"""Here is what i did in the last 20 days. analyse this data and convert it into some actionable steps that i can take to improve. ***Motivation start*** {prog} ***Motivation end***"""
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    res = model.generate_content(query)
    return res.text

def stream_write(text):
    for i in text.split(" "):
        yield i + " "
col1,col2, col3 = st.columns([1,3,1])
sug = col1.button("Get Suggestions")
mot = col3.button("Get Motivation")
if sug:
    text = Get_inp_sug()
    st.write_stream(stream_write(text))
if mot:
    text = Get_Motivation()
    st.write_stream(stream_write(text))


# st.write(data)