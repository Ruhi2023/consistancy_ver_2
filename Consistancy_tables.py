from mysql import connector
import streamlit as st
import os
# i am checking if database exists
dbname = 'consistancy'

a_conn = connector.connect(
    host = 'localhost',
    user = 'Ruhi',
    passwd = 'Ruhi@5084'
)

cur = a_conn.cursor()
cur.execute(f"Show Databases")
res = cur.fetchall()
if (dbname,) in res:
    print("Database exists")
else:
    cur.execute(f"Create Database {dbname}")
    print("Database created")
    a_conn.commit()

a_conn.close()

the_db_conn = connector.connect(
    host = 'localhost',
    user = 'Ruhi',
    passwd = 'Ruhi@5084',
    database = dbname
)

cur = the_db_conn.cursor()

# Query_create_my_progress = """
# create table if not exists my_progress (
#     Today datetime Default current_timestamp primary key,
#     The_topic VARCHAR(255),
#     The_test_result INT,
#     The_suggestion TEXT)
# """
Query_create_my_progress = """
CREATE TABLE if not exists my_progress (
    Today datetime Default current_timestamp,
    topic_id int,
    test_id int,
    Foreign key(topic_id) REFERENCES Topics(Topic_id),
    Foreign key(test_id) REFERENCES Tests(Test_id),
    Method_Summary_User text,
    Method_Summary_Sugg text,
    What_did_i_lack text
)
"""
Query_create_struggles = """
CREATE TABLE if not exists struggles (
    The_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP primary key,
    The_struggle TEXT,
    The_suggestion TEXT
)
"""
Query_create_ideas_table = """
CREATE TABLE if not exists ideas (
    The_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP primary key,
    Category VARCHAR(255),
    Idea_heading VARCHAR(255),
    Idea_description TEXT,
    Implementable BOOLEAN,
    Status ENUM('implemented', 'implementing', 'understood', 'understanding', 'not reached')
)
"""
Query_create_Questions_table = """
CREATE TABLE if not exists Questions (
    the_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    question TEXT,
    question_no INT check(question_no <=30),
    question_type VARCHAR(255) check(question_type In('easy', 'medium', 'difficult')),
    user_Answer TEXT default NULL,
    topic_id int,
    test_id int,
    Foreign key(topic_id) REFERENCES Topics(topic_id),
    Foreign key(test_id) REFERENCES Tests(test_id),
    correctness BOOLEAN) """
Query_Create_Tests_table = """
CREATE TABLE if not exists Tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    easy_Questions int,
    medium_Questions int,
    difficult_Questions int,
    topic_id int,
    Foreign key(topic_id) REFERENCES Topics(topic_id),
    score int check(score <=100),
    suggestions TEXT
)"""
Query_Create_topics_table = """
CREATE TABLE if not exists Topics (
    topic_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_name VARCHAR(255) UNIQUE,
    topic_type VARCHAR(255) check(topic_type In('skills', 'projects','ideas_implementation')),
    topic_description TEXT default NULL
)"""
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
the_db_conn.commit()
the_db_conn.close()

def connnecting():
    db = connector.connect(
        host = 'localhost',
        user = 'Ruhi',
        passwd = 'Ruhi@5084',
        database = dbname,
        connection_timeout=3600
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
