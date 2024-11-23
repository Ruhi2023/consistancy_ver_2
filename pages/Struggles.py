import streamlit as st 
import google.generativeai as gai 
import Consistancy_tables as su
import os
import time
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
    gai.configure(api_key=api_key_from_func)
# i want to get cofigrations of friend from the cur_dir + //Assets//Friends//name.txt 

@st.dialog("Get my friend")
def get_name():
    if not os.path.exists(os.path.join(os.getcwd(), "Assets", "Friends")):
        os.makedirs(os.path.join(os.getcwd(), "Assets", "Friends"))
    path_to_sora = os.path.join(os.getcwd(), "Assets", "Friends")
    list_of_friends = os.listdir(path_to_sora) 
    
    if len(list_of_friends) == 0:
        # get input from user and save it in name.txt file
        set_friend= st.form("Define your friend")
        name = set_friend.text_input("What is your friend's name?")
        attrib = set_friend.text_area("What is your friend like Explain in detail")
        thatsit = set_friend.form_submit_button("That is all")
        if thatsit and name != "" and attrib != "":
            with open(os.path.join(path_to_sora, f"{name}.txt"), "w") as f:
                f.write(f"You are {name}.\nBelow is the {name}'s description\n")
                f.write(attrib)
            st.success("Friend added")
        else:
            st.error("Please fill all the fields")
        st.session_state["friend_file"] = os.path.join(path_to_sora, f"{name}.txt")
    elif len(list_of_friends) >= 1:
        # select the friend and then return the path
        if "Add new friend" not in list_of_friends:
            list_of_friends.append("Add new friend")
        
        fr_name = st.selectbox("Select your friend", list_of_friends)
        if fr_name == "Add new friend":
            set_friend= st.form("Define your friend")
            name = set_friend.text_input("What is your friend's name?")
            attrib = set_friend.text_area("What is your friend like Explain in detail")
            thatsit = set_friend.form_submit_button("That is all")
            if thatsit and name != "" and attrib != "":
                with open(os.path.join(path_to_sora, f"{name}.txt"), "w") as f:
                    f.write(f"You are {name}.\nBelow is the {name}'s description\n")
                    f.write(attrib)
                st.success("Friend added")
            else:
                st.error("Please fill all the fields")
            st.session_state["friend_file"] = os.path.join(path_to_sora, f"{name}.txt")
        else:
            st.session_state["friend_file"] =  os.path.join(path_to_sora, fr_name)
    


    
 
        
sbar = st.sidebar

sbar.button("Get friend", on_click=get_name)

# st.session_state 
def get_answer(prompt):
    generation_config = {
          "temperature": 0.9,
          "top_p": 0.95,
          "top_k": 64,
          "max_output_tokens": 8192,
          "response_mime_type": "text/plain",
        }
    model = gai.GenerativeModel(model_name="gemini-1.5-flash",generation_config=generation_config)
    if "friend_file" in st.session_state:
        with open(st.session_state.friend_file, "r") as f:
            discreption = f.read()
    else:    
        discreption = "You are Sora."
    addition = f"""You need to act as [person/role]. Here is the description: {discreption}. I will provide you with the user's chat history and their current question. Please assess whether there are any areas in which the user (provided for as role:user) can improve.
If you identify an opportunity for improvement, provide a suggestion enclosed within the special markers #IMPSUG:STA# and #IMPSUG:END#. 
However, only include a suggestion if you find a meaningful area for improvement—don't suggest changes for every message, only when there's a clear opportunity for enhancement.
"""
    if len(st.session_state.chat_hist_stru) > 8:
        prev = st.session_state.chat_hist_stru[-8:]
    else:
        prev = st.session_state.chat_hist_stru
    res = model.generate_content([str({"CONTEXT for refrence not needed in reply ": addition}),str({" CHAT HISTORY For refrence, HISTORY not needed in reply":prev}), str({"user's MESSAGE you need to reply as the acting as the person provided for in context":prompt})])
    print(res.usage_metadata)
    return res.text

@st.dialog("Add Suggestion")
def see_for_improvement(suggestion, strug):
    
    
    st.write(suggestion)
    col1,col2,col3 = st.columns([1,3,1])
    if col1.button("Yes"):
        try:
            My_db, My_cur = su.connnecting()
            uery = "INSERT INTO struggles (The_struggle, The_suggestion) VALUES (%s, %s)" # (strug, suggestion))
            tup = (strug, suggestion)
            My_cur.execute(uery, tup)
            My_db.commit()
            st.success(f"Query executed {uery}")
        except Exception as e:
            st.error(f"Query not executed {uery}, beacuse {e}")
            print(e)
        finally:
            My_db.close()
            time.sleep(3)
            st.rerun()

    if col3.button("Discard"):
        st.rerun()
        
                


if 'chat_hist_stru' not in st.session_state:
    st.session_state.chat_hist_stru = []
# display the chat messages 
for message in st.session_state.chat_hist_stru:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
# reacting to user input
if usr_strug := st.chat_input("Tell me what you did today"):
    #display message to the page
    with st.chat_message("user"):
        st.markdown(usr_strug)
    
    # append it to st.session_state.chat_hist_stru
    st.session_state.chat_hist_stru.append({"role":"user","content":usr_strug})

    # get the answer
    answer = get_answer(usr_strug)
    assistant_name = os.path.basename(st.session_state.friend_file)
    # display the answer
    with st.chat_message(assistant_name):
        st.markdown(answer)

    

    # append it to st.session_state.chat_hist_stru
    st.session_state.chat_hist_stru.append({"role":assistant_name,"content":answer})
    if "#IMPSUG:STA#" in answer and "#IMPSUG:END#" in answer:
        if "#IMPSUG:STA#" in answer and "#IMPSUG:END#" in answer:
            ind_end = answer.index("#IMPSUG:END#")
            ind_sta = answer.index("#IMPSUG:STA#")
            suggestion = answer[ind_sta+11:ind_end]
        else:
            suggestion = answer

        see_for_improvement(suggestion, usr_strug)

# st.session_state