import streamlit as st
def nav_generator():
    if "authenticated_user" in st.session_state:
        nav = st.navigation({
    "Home": [st.Page("pages/Main_app.py", title="Home", icon="🏠"),st.Page("pages/User_profile.py",title="My Profile",icon = "🌱")],
    "Evaluation": [st.Page("pages/project_evaluation.py", title="Practical Testing", icon="👨‍💻"), st.Page("pages/Testing_screen_2_temp.py", title="SKILL Testing", icon="📚")],
    "Improvement":[st.Page("pages/Idea_management.py", title="Ideas", icon="💡"), st.Page("pages/Struggles.py", title = "Chat", icon="💬"), st.Page("pages/Improv_sug.py", title="Summary", icon="📈")],
})
    elif "authenticated_user" not in st.session_state:
        nav = st.navigation({
    "login": [st.Page("pages/login.py", title="Login", icon="🔑"),st.Page("pages/register.py",title="Register", icon="#️⃣")],})
    return nav

nav = nav_generator()
nav.run()