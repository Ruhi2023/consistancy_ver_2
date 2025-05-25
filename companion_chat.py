import utilities as u
# import Consistancy_tables_with_orm as su
# import langchain_google_genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# import streamlit as st
import os
import datetime as dt 
from langchain_milvus import Milvus
from pymilvus import DataType, connections,utility, db, Collection, MilvusException


# features
# A. create a new companion or firend
# B. chat 
#   B.A. Memories (milvus and rag)
#   B.B. tool for entering user struggles in database
#   B.C. different companions

# work-flow
# 1. Create milvis db/ client if not exisit, create a collection in it same (ionly if it does not exist)
# 1.1 
# 2. make agent from models and give it tools
# 2.1 agent class with tools
#   2.1.1 put memory
#   2.1.2 get memory (rag milvus)
#   2.1.3 refine prompt (refine the databse prompt)
#   2.1.4 ChatAnswer (will actually reply to chat)
# 2.2 the above flow is a bit flawed, i wnat each user message to be replied to but there must be some backend functionallity


# 3. build ui
# 3.1 auto save chat in db
# 3.2 show chat history different for different friends

# seg-expl creating the vector store database

def create_db_Consistancy_postgres():
    connections.connect("default", host="127.0.0.1", port=19530)
    print("Connected to Milvus")
    dbs =db.list_database()
    if "consistancy2" in dbs:
        print("Database exists")
        db.using_database("consistancy2")
    else:
        db.create_database("consistancy2")
        db.using_database("consistancy2")
        print("Database created")
    print(db.list_database())
    print("using database {db_description}".format(db_description = db.describe_database("consistancy2")))
    return connections


    
conn = create_db_Consistancy_postgres()
collections = db.list_database()

print(collections) 
col = conn.list_connections()

print(col)

from pymilvus import MilvusClient

client = MilvusClient(uri="http://localhost:19530", db_name="consistancy2")

collections = client.list_collections()
print("Collections:", collections)
# memory_schema = client.create_schema()
# memory_schema.add_field(field_name="memory_text", datatype=DataType.VARCHAR, max_length=int(65535/2))
# memory_schema.add_field(field_name="memory_title", datatype=DataType.VARCHAR, max_length=100)
# memory_schema.add_field(field_name="Memory_embedding",datatype= DataType.FLOAT_VECTOR, dim=768 )
# client.create_collection("Memories_test",
#                          schema=memory_schema,
#                          auto_id=True,
#                          )

 

class ChatAgent:
    def __init__(self):
        self.cur_chat = {}
        g_auth = u.GoogleGenAIUtilities()
        
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=g_auth.api_key)
        self.llm = g_auth.give_the_chatmodel()
        self.vector_store = Milvus(embedding_function=self.embeddings, connection_args={"uri": "http://localhost:19530", "db_name": "consistancy2"}, index_params={"index_type": "FLAT", "metric_type": "L2"}, collection_name="Memories_test")
        print(self.vector_store.collection_description)
    
    def add_collection_if_not_exist(self):
        collections = db.list_database()
        if "consistancy2" in collections:
            print("Database exists")
            db.using_database("consistancy2")
        else:
            db.create_database("consistancy2")
            db.using_database("consistancy2")
            print("Database created")
        print(db.list_database())
        print("using database {db_description}".format(db_description = db.describe_database("consistancy2")))
        
agent = ChatAgent()

