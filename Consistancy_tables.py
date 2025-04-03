# from mysql import connector
from psycopg2 import connect
import streamlit as st
import os
import json
# i am checking if database exists

def getconnnames():
    path = os.path.join(os.getcwd(), "Assets", "db_details.json")
    with open(path, 'r',encoding='utf-8') as f:
        data = json.load(f)
    db = "consistancy"
    host = data['host']
    user = data['user']
    passwd = data['password']
    return (host, user, passwd,db)
my_host, my_user, my_passwd, dbname = getconnnames()
a_conn = connect(
    host = my_host,
    user = my_user,
    password = my_passwd
)

cur = a_conn.cursor()
a_conn.autocommit = True
cur.execute(f"SELECT datname FROM pg_database;")
res = cur.fetchall()
if (dbname,) in res:
    print("Database exists")
else:
    
    
    cur.execute(f"Create Database {dbname}")
    print("Database created")
    a_conn.commit()

a_conn.close()

the_db_conn = connect(
    host = my_host,
    user = my_user,
    password = my_passwd,
    database = dbname
)

cur = the_db_conn.cursor()


# Query_create_my_progress = """
# CREATE TABLE if not exists my_progress (
#     Today datetime Default current_timestamp,
#     topic_id int,
#     test_id int,
#     Foreign key(topic_id) REFERENCES Topics(Topic_id),
#     Foreign key(test_id) REFERENCES Tests(Test_id),
#     Method_Summary_User text,
#     Method_Summary_Sugg text,
#     What_did_i_lack text,
#     workflow_qs int check(workflow_qs >= 6 and workflow_qs <= 21)
# )
# """
# * topic id in the above table will only be for project/practials topics
Query_create_my_progress = """
CREATE TABLE IF NOT EXISTS my_progress (
    Today TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic_id INT,
    test_id INT,
    FOREIGN KEY (topic_id) REFERENCES Topics(topic_id),
    FOREIGN KEY (test_id) REFERENCES Tests(test_id),
    Method_Summary_User TEXT,
    Method_Summary_Sugg TEXT,
    What_did_i_lack TEXT,
    workflow_qs INT CHECK (workflow_qs >= 6 AND workflow_qs <= 21)
)
"""

Query_create_struggles = """
CREATE TABLE IF NOT EXISTS struggles (
    The_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
    The_struggle TEXT,
    The_suggestion TEXT
)
"""

Query_create_workflow_qs = """
CREATE TABLE IF NOT EXISTS workflow_questions (
    The_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Question_no INT CHECK (Question_no <= 21),
    Question TEXT,
    User_Answer TEXT,
    topic_id INT,
    FOREIGN KEY (topic_id) REFERENCES Topics(topic_id),
    test_id INT,
    FOREIGN KEY (test_id) REFERENCES Tests(test_id),
    CONSTRAINT specific_question PRIMARY KEY (Question_no, topic_id, test_id)
)
"""

Query_create_ideas_table = """
CREATE TABLE IF NOT EXISTS ideas (
    The_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
    Category VARCHAR(255),
    Idea_heading VARCHAR(255),
    Idea_description TEXT,
    Implementable BOOLEAN,
    Status VARCHAR(20) CHECK (Status IN ('implemented', 'implementing', 'understood', 'understanding', 'not reached'))
)
"""

Query_create_Questions_table = """
CREATE TABLE IF NOT EXISTS Questions (
    the_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    question TEXT,
    question_no INT CHECK (question_no <= 30),
    question_type VARCHAR(255) CHECK (question_type IN ('easy', 'medium', 'difficult')),
    user_Answer TEXT DEFAULT NULL,
    topic_id INT,
    test_id INT,
    FOREIGN KEY (topic_id) REFERENCES Topics(topic_id),
    FOREIGN KEY (test_id) REFERENCES Tests(test_id),
    correctness BOOLEAN,
    CONSTRAINT UC_QUE UNIQUE (question_no, test_id, question_type)
)
"""

Query_Create_Tests_table = """
CREATE TABLE IF NOT EXISTS Tests (
    test_id SERIAL PRIMARY KEY,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    easy_Questions INT,
    medium_Questions INT,
    difficult_Questions INT,
    topic_id INT,
    FOREIGN KEY (topic_id) REFERENCES Topics(topic_id),
    score INT CHECK (score <= 100),
    suggestions TEXT
)
"""

Query_Create_topics_table = """
CREATE TABLE IF NOT EXISTS Topics (
    topic_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic_id SERIAL PRIMARY KEY,
    topic_name VARCHAR(255) UNIQUE,
    topic_type VARCHAR(255) CHECK (topic_type IN ('skills', 'projects', 'ideas_implementation')),
    topic_description TEXT DEFAULT NULL
)
"""

cur.execute(Query_Create_topics_table)
the_db_conn.commit()
print("Topics table created")
cur.execute(Query_Create_Tests_table)
the_db_conn.commit()
print("Tests table created")
cur.execute(Query_create_Questions_table)
the_db_conn.commit()
print("Questions table created")
cur.execute(Query_create_my_progress)
cur.execute(Query_create_struggles)
cur.execute(Query_create_ideas_table)
cur.execute(Query_create_workflow_qs)
the_db_conn.commit()
the_db_conn.close()

def connnecting(host = my_host, user=my_user, passwd = my_passwd,database =dbname):
    db = connect(
        host = my_host,
        user = my_user,
        password = my_passwd,
        database = dbname
    )

    cur = db.cursor()
    return db,cur

print("""connect_to_db""")
def get_mykey():
    """ Function for getting api key"""
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
