from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import text
import os
import json
import datetime

# Create a base class for our models
Base = declarative_base()

# Define our models
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    passwd = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    last_login = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    topics = relationship("Topic", back_populates="user")
    tests = relationship("Test", back_populates="user")
    my_progress = relationship("MyProgress", back_populates="user")
    struggles = relationship("Struggle", back_populates="user")
    workflow_questions = relationship("WorkflowQuestion", back_populates="user")
    ideas = relationship("Idea", back_populates="user")
    questions = relationship("Question", back_populates="user")
    friends = relationship("Friend", back_populates="user")
    memories = relationship("Memory", back_populates="user")

class Topic(Base):
    __tablename__ = 'topics'
    
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_start_date = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    topic_name = Column(String(255), unique=True, nullable=False)
    topic_type = Column(String(255), nullable=False)
    topic_description = Column(Text, nullable=True)
    
    # Add check constraint for topic_type
    __table_args__ = (
        CheckConstraint("topic_type IN ('skills', 'projects', 'ideas_implementation')"),
    )
    
    # Relationships
    user = relationship("User", back_populates="topics")
    tests = relationship("Test", back_populates="topic")
    my_progress = relationship("MyProgress", back_populates="topic")
    workflow_questions = relationship("WorkflowQuestion", back_populates="topic")
    questions = relationship("Question", back_populates="topic")

class Test(Base):
    __tablename__ = 'tests'
    
    test_id = Column(Integer, primary_key=True, autoincrement=True)
    test_date = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    easy_questions = Column(Integer, default=0)
    medium_questions = Column(Integer, default=0)
    difficult_questions = Column(Integer, default=0)
    topic_id = Column(Integer, ForeignKey('topics.topic_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    score = Column(Integer, nullable=True)
    suggestions = Column(Text, nullable=True)
    
    # Add check constraint for score
    __table_args__ = (
        CheckConstraint("score <= 100"),
    )
    
    # Relationships
    user = relationship("User", back_populates="tests")
    topic = relationship("Topic", back_populates="tests")
    my_progress = relationship("MyProgress", back_populates="test")
    workflow_questions = relationship("WorkflowQuestion", back_populates="test")
    questions = relationship("Question", back_populates="test")

class MyProgress(Base):
    __tablename__ = 'my_progress'
    
    # Note: This table doesn't have a single primary key in your SQL definition
    # I'll use a composite primary key based on the relationships
    today = Column(TIMESTAMP(timezone=True), server_default=text('now()'), primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id') )
    test_id = Column(Integer, ForeignKey('tests.test_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    method_summary_user = Column(Text,nullable=True)
    method_summary_sugg = Column(Text,nullable=True)
    what_did_i_lack = Column(Text,nullable=True)
    workflow_qs = Column(Integer,nullable=True)
    
    # Add check constraint for workflow_qs
    __table_args__ = (
        CheckConstraint("workflow_qs >= 6 AND workflow_qs <= 21"),
    )
    
    # Relationships
    user = relationship("User", back_populates="my_progress")
    topic = relationship("Topic", back_populates="my_progress")
    test = relationship("Test", back_populates="my_progress")

class Struggle(Base):
    __tablename__ = 'struggles'
    
    the_date = Column(TIMESTAMP(timezone=True), default=text('now()'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    the_struggle = Column(Text, nullable=True)
    the_suggestion = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="struggles")

class WorkflowQuestion(Base):
    __tablename__ = 'workflow_questions'
    
    the_date = Column(TIMESTAMP(timezone=True), default=text('now()'))
    question_no = Column(Integer, primary_key=True)
    question = Column(Text)
    user_answer = Column(Text, nullable=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id'),primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'),primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.test_id'),primary_key=True)
    
    # Add check constraint for question_no
    __table_args__ = (
        CheckConstraint("question_no <= 21"),
    )
    
    # Relationships
    user = relationship("User", back_populates="workflow_questions")
    topic = relationship("Topic", back_populates="workflow_questions")
    test = relationship("Test", back_populates="workflow_questions")

class Idea(Base):
    __tablename__ = 'ideas'
    
    the_date = Column(TIMESTAMP(timezone=True), default=text('now()'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    category = Column(String(255))
    idea_heading = Column(String(255))
    idea_description = Column(Text)
    implementable = Column(Boolean)
    status = Column(Enum('implemented', 'implementing', 'understood', 'understanding', 'not reached', name='idea_status'))
    
    # Relationships
    user = relationship("User", back_populates="ideas")

class Question(Base):
    __tablename__ = 'questions'
    
    the_date = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    question = Column(Text)
    question_no = Column(Integer, primary_key=True)
    question_type = Column(String(255))
    user_answer = Column(Text, nullable=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id'),primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.test_id'),primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'),primary_key=True)
    correctness = Column(Boolean, nullable=True)
    
    # Add constraints
    __table_args__ = (
        CheckConstraint("question_no <= 30"),
        CheckConstraint("question_type IN ('easy', 'medium', 'difficult')"),
        UniqueConstraint('question_no', 'test_id', 'question_type', name='UC_QUE')
    )
    
    # Since there's no explicit primary key, we'll make a composite one
    # SQLAlchemy requires a primary key
    __mapper_args__ = {
        'primary_key': [question_no, test_id, question_type]
    }
    
    # Relationships
    user = relationship("User", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    test = relationship("Test", back_populates="questions")

class Friend(Base):
    __tablename__ = 'friends'
    
    friend_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    friend_name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    is_public = Column(Boolean, default=False)
    last_accessed = Column(TIMESTAMP(timezone=True))
    last_updated = Column(TIMESTAMP(timezone=True))
    friend_prompt = Column(Text)
    friend_role = Column(String(255), default='General Friend')
    
    # Relationships
    user = relationship("User", back_populates="friends")
    memories = relationship("Memory", back_populates="friend")

class Memory(Base):
    __tablename__ = 'memories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    friend_id = Column(Integer, ForeignKey('friends.friend_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    memory_type = Column(String(255))
    memory_content = Column(Text)
    memory_created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    memory_updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    memory_accessed_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    memory_title = Column(String(255))
    id_reference_milvus = Column(Integer)
    
    # Add check constraint for memory_type
    __table_args__ = (
        CheckConstraint("memory_type IN ('likes', 'dislikes', 'bonding_event', 'struggles')"),
    )
    
    # Relationships
    user = relationship("User", back_populates="memories")
    friend = relationship("Friend", back_populates="memories")
class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    chat_date = Column(TIMESTAMP(timezone=True), default=text('now()'))
    chat_data = Column(JSON)
# Database connection function
def get_connection_details():
    path = os.path.join(os.getcwd(), "Assets", "db_details.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    db = "consistancy2"
    host = data['host']
    user = data['user']
    passwd = data['password']
    return host, user, passwd, db

def create_session():
    host, user, passwd, db = get_connection_details()
    
    # Create connection string
    connection_string = f"postgresql://{user}:{passwd}@{host}/{db}"
    
    # Create engine and session
    engine = create_engine(connection_string)
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session

def connecting_connector():
    host, user, passwd, db = get_connection_details()
    import psycopg2 as pg
    db_con = pg.connect(f"postgresql://{user}:{passwd}@{host}/{db}")
    cur = db_con.cursor()
    return db_con, cur

