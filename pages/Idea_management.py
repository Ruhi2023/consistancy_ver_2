import streamlit as st 
import datetime as dt 
import Consistancy_tables as su 
import time

def fetch_status_counts():
    the_db, cursor = su.connnecting()
    
    query = """
    SELECT Status, COUNT(*) as count
    FROM ideas
    GROUP BY Status
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    cursor.close()
    the_db.close()
    
    # Return the counts as a dictionary
    status_counts = {status: count for status, count in results}
    return status_counts

# Function to display the tree structure
def display_tree_structure():
    

    # Fetch status counts from the database
    status_counts = fetch_status_counts()
    
    # Display the tree structure using indents to simulate a hierarchy
    st.write("📁 Ideas")
    
    # First level: All ideas
    total_ideas = sum(status_counts.values())
    st.write(f"├── Total Ideas: {total_ideas}")
    
    # Second level: Categories of statuses
    for status, count in status_counts.items():
        icon = "📌"  # Customize icon per status if you want
        st.write(f"    ├── {icon} {status.capitalize()}: {count} ideas")
    
    st.write("    └── End of status tree")


def manage_callback(upd,heading, disc, implementable,status, category, id_of_idea):
    My_db, My_cur = su.connnecting()
    if upd == "Yes":
        print("updating")
        if id_of_idea is not None:
            upd_query = "update ideas set Category = %s, Idea_heading = %s, Idea_description = %s, Implementable = %s, Status = %s where The_date = %s"
            tup = (str(category),str(heading), str(disc), implementable, str(status), dt.datetime.strftime(id_of_idea, format="%Y-%m-%d %H:%M:%S"))
            try:
                My_cur.execute(upd_query, tup)
                My_db.commit()
                
                st.success(f"Query executed {upd_query}")
            except Exception as e:
                st.error(f"Query not executed {upd_query}, beacuse {e}")
            finally:
                My_db.close()
    elif upd == "No":
        print("creating")
        time.sleep(1)
        insert_query = "insert into ideas (Idea_heading, Idea_description, Category, Implementable, Status) values (%s, %s, %s, %s, %s)"
        try:
            My_cur.execute(insert_query, (str(heading), str(disc), str(category), implementable, str(status)))
            My_db.commit()
            st.success(f"Query executed {insert_query}", icon="✅")
        except Exception as e:
            st.error(f"Query not executed {insert_query}, beacuse {e}")
        finally:
            My_db.close()

st.title("Idea Status Overview")
Col1,col2 = st.columns([1,3])

with Col1:
    display_tree_structure()

with col2:
    form_selector = st.radio("Do you want to update an existing idea?", ("Yes", "No"))
    # create convertable from with a radio button 
    with st.form("convertable_form"):
        update_existing = form_selector
        if update_existing == "Yes":
            st.write("Update an existing idea")
            My_db, My_cur = su.connnecting()
            My_cur.execute("SELECT * FROM ideas")
            ideas = My_cur.fetchall()
            idea_name = st.selectbox("Select an idea", ideas)
            st.write(f"you selected {idea_name}, It has id of {idea_name[0]}")
            id_idea = idea_name[0]
            # input the value for components
        elif update_existing == "No":
            st.write("Create new idea")
            id_idea = None
        heading = st.text_input("Heading")
        description = st.text_area("Description")
        category= st.text_input("Category")
        implementable = st.checkbox("Check if Idea is implementable, leave blank if idea can be understood")
        status = st.selectbox("Select status", ('implemented','implementing','understood','understanding','not reached'))
        submit = st.form_submit_button("Submit")
        if submit:
            manage_callback(update_existing,heading, description, implementable, status, category, id_idea)