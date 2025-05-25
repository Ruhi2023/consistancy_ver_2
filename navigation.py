import streamlit as st

import base64

def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


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

image_path = "D:\my work\project\consistancy_migrating_from_prototype\consistancy_ver_2\Assets\imgs\consistency2.png"
img_path2 = "D:\my work\project\consistancy_migrating_from_prototype\consistancy_ver_2\Assets\imgs\consistancy2.png"
set_background(img_path2)
nav = nav_generator()
nav.run()