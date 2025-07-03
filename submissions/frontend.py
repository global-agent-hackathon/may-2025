import streamlit as st
import sqlite3
import os
from videoChatbot import process_video_and_query, process_video
from pathlib import Path
from read_env import *
import langchain
from RecommendationAgent import recommendationTool
import pandas as pd
import uuid
import time
langchain.verbose = False

# Import required LangChain modules
from langchain.document_loaders import PyPDFLoader,Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import pickle
from langchain.chains import RetrievalQA


# ---------- Database Functions ----------
def init_db():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id TEXT PRIMARY KEY,
            name VARCHAR(50),
            email NVARCHAR(50),
            age INTEGER,
            phone_number NVARCHAR(50)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Skills (
            user_id VARCHAR(50),
            skill_name VARCHAR(100),
            skill_proficiency VARCHAR(50),
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LearningGoal (
            user_id VARCHAR(50),
            goal_name VARCHAR(100),
            goal_proficiency VARCHAR(50),
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Topic (
            user_id VARCHAR(50),
            topic_name VARCHAR(100),
            topic_proficiency VARCHAR(50),
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
    """)

    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    user_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO User (id, name, email, age, phone_number)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, data['name'], data['email'], data['age'], data['phone']))

    for skill in data['skills']:
        cursor.execute("""
            INSERT INTO Skills (user_id, skill_name, skill_proficiency)
            VALUES (?, ?, ?)
        """, (user_id, skill['name'], skill['level']))

    goal = data['learning_goal']
    cursor.execute("""
        INSERT INTO LearningGoal (user_id, goal_name, goal_proficiency)
        VALUES (?, ?, ?)
    """, (user_id, goal['goal'], goal['desired_proficiency']))

    for topic in data['topics_to_learn']:
        cursor.execute("""
            INSERT INTO Topic (user_id, topic_name, topic_proficiency)
            VALUES (?, ?, ?)
        """, (user_id, topic['name'], topic['level']))

    conn.commit()
    conn.close()
    


def get_user_profile(name):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    # Fetch user basic info
    cursor.execute("SELECT id, name, email, age, phone_number FROM User WHERE name = ?", (name,))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        return None

    user_id, name, email, age, phone = user_row

    # Fetch skills
    cursor.execute("SELECT skill_name, skill_proficiency FROM Skills WHERE user_id = ?", (user_id,))
    skills = [{"name": row[0], "level": row[1]} for row in cursor.fetchall()]

    # Fetch learning goal
    cursor.execute("SELECT goal_name, goal_proficiency FROM LearningGoal WHERE user_id = ?", (user_id,))
    goal_row = cursor.fetchone()
    learning_goal = {"goal": goal_row[0], "desired_proficiency": goal_row[1]} if goal_row else {}

    # Fetch topics
    cursor.execute("SELECT topic_name, topic_proficiency FROM Topic WHERE user_id = ?", (user_id,))
    topics = [{"name": row[0], "level": row[1]} for row in cursor.fetchall()]

    conn.close()

    return {
        "name": name,
        "email": email,
        "age": age,
        "phone": phone,
        "skills": skills,
        "learning_goal": learning_goal,
        "topics_to_learn": topics
    }

# ---------- Streamlit App ----------
# Initialize the database
init_db()
conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()
user_df = pd.read_sql_query("SELECT id, name FROM User;", conn)
user_names = user_df["name"].tolist()
print("*****1",user_names)
goal_query = f"SELECT goal_name, goal_proficiency FROM LearningGoal;"
goal_df = pd.read_sql_query(goal_query, conn)
print("*****2",goal_df)
topic_query = f"SELECT topic_name, topic_proficiency FROM Topic;"
topic_df = pd.read_sql_query(topic_query, conn)
print("*****3",topic_df)

if 'skills' not in st.session_state:
    st.session_state.skills = []
if 'topics' not in st.session_state:
    st.session_state.topics = []

# Global cache for index
if "index_cache" not in st.session_state:
    st.session_state.index_cache = {}

# Dummy chatbot function using actual logic
def dummy_chat_response(query, index):
    return process_video_and_query(query, index)

# ---- UI START ----
st.set_page_config(layout="wide")
# tabs = st.tabs(["Register Profiles", "Topic-Based Recommendation", "Chatbot with Resources", "Profile-Based Recommendations","My Profile"])
# tabs = st.tabs(["My Profile", "Topic-Based Recommendation", "Chatbot with Resources", "Admin","Profile-Based Recommendations"])
tabs = st.tabs(["My Profile", "Topic-Based Recommendation", "Chatbot with Resources"])

# ---- Tab 2: Recommendation ----
with tabs[1]:
    st.header("🧠 Personalized Learning Recommendations")

    st.markdown("Enter a topic and select your proficiency level to get curated resources (YouTube tutorials and websites).")

    # Input fields
    topic = st.text_input("Enter Topic", placeholder="e.g., Machine Learning")
    proficiency_level = st.selectbox("Select Proficiency Level", ["Beginner", "Intermediate", "Advanced"])

    # Button to trigger recommendation
    if st.button("Get Recommendations"):
        if topic.strip() == "":
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Fetching recommendations..."):
                try:
                    recommendations = recommendationTool(topic, proficiency_level)
                    st.markdown("### 📚 Recommendations")
                    st.markdown(recommendations)
                except Exception as e:
                    st.error(f"An error occurred while fetching recommendations: {e}")

# ---- Tab 3: Chatbot with Resources ----
with tabs[2]:
    st.header("Chatbot with Resources")

    # Load Videos and PDFs
    video_folder = "Youtube videos"
    pdf_folder = "pdfs"
    video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    # Select a video for chat interaction
    st.subheader("🎬 Available Videos")
    selected_video = st.selectbox("Select a video to open chat", ["-- Select --"] + video_files)

    if selected_video != "-- Select --":
        st.video(os.path.join(video_folder, selected_video))

        # Process the video only once and cache the index
        if selected_video not in st.session_state.index_cache:
            with st.spinner("🤖 Chatbot is loading... Please wait."):
                index = process_video(selected_video)
                st.session_state.index_cache[selected_video] = index
                st.success("Chatbot is ready!")
        else:
            index = st.session_state.index_cache[selected_video]
            st.success("Chatbot is ready!")

        st.markdown("### 🤖 Chat with Bot about this Video")
        user_query = st.text_input("Ask a question:")
        if st.button("Submit"):
            if user_query.strip():
                response = dummy_chat_response(user_query, index)
                st.success(response)
            else:
                st.warning("Please enter a question.")

    st.markdown("---")

    # ---- 📄 PDF Chatbot ----
    st.subheader("📄 PDF Materials")
    selected_pdf = st.selectbox("Select a PDF to open chat", ["-- Select --"] + [pdf.replace(".pdf", "") for pdf in pdf_files])

    if selected_pdf != "-- Select --":
        if selected_pdf not in st.session_state.index_cache:
            with st.spinner("🔍 Processing PDF and setting up chatbot..."):
                # Embed and set up retriever once
                def prepare_pdf_retriever(doc_name):
                    # Dummy query just to trigger full retriever return instead of immediate response
                    file_path = f"{pdf_folder}/{doc_name}.pdf"
                    loader = PyPDFLoader(file_path)
                    pages = loader.load_and_split()
                    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                    docs = text_splitter.split_documents(pages)
                    retriever = FAISS.from_documents(docs, EMBEDDINGS_MODEL).as_retriever()
                    return retriever

                retriever = prepare_pdf_retriever(selected_pdf)
                qa = RetrievalQA.from_chain_type(llm=LLM_MODEL_GPT3, chain_type='stuff', retriever=retriever)
                st.session_state.index_cache[selected_pdf] = qa
                st.success("PDF Chatbot is ready!")
        else:
            qa = st.session_state.index_cache[selected_pdf]
            st.success("PDF Chatbot is ready!")

        st.markdown("### 🧠 Chat with Bot about this PDF")
        pdf_query = st.text_input("Ask a question about the PDF:", key="pdf_query")
        if st.button("Submit PDF Query"):
            if pdf_query.strip():
                response = qa.run(pdf_query)
                print( "RESPONSE",response)
                st.success(response)
            else:
                st.warning("Please enter a question.")

with tabs[0]:
    # st.header("My Profile & Recommendations")

    col1, col2 = st.columns(2)

    # --- LEFT PANE: My Profile ---
    with col1:
        st.subheader("👤 My Profile")
        profile_data = get_user_profile("Sinegalatha B")

        # Initialize edit mode
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False

        if not profile_data:
            st.warning("Profile for Sinegalatha B not found.")
        else:
            if st.session_state.edit_mode:
                with st.form("edit_profile_form"):
                    st.text_input("Name", value=profile_data["name"], key="edit_name")
                    st.text_input("Email", value=profile_data["email"], key="edit_email")
                    st.number_input("Age", min_value=0, step=1, value=profile_data["age"], key="edit_age")
                    st.text_input("Phone Number", value=profile_data["phone"], key="edit_phone")
                    st.subheader("Skills")
                    skills = [st.text_input(f"Skill {i+1} Name", value=skill["name"], key=f"edit_skill_{i}_name") for i, skill in enumerate(profile_data["skills"])]
                    skill_levels = [st.selectbox(f"Skill {i+1} Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(skill["level"]), key=f"edit_skill_{i}_level") for i, skill in enumerate(profile_data["skills"])]
                    st.subheader("Learning Goal")
                    st.text_input("Goal", value=profile_data["learning_goal"]["goal"], key="edit_goal")
                    st.selectbox("Desired Proficiency", ["Beginner", "Intermediate", "Advanced"],
                                 index=["Beginner", "Intermediate", "Advanced"].index(profile_data["learning_goal"]["desired_proficiency"]),
                                 key="edit_goal_proficiency")
                    st.subheader("Topics to Learn")
                    topics = [st.text_input(f"Topic {i+1} Name", value=topic["name"], key=f"edit_topic_{i}_name") for i, topic in enumerate(profile_data["topics_to_learn"])]
                    topic_levels = [st.selectbox(f"Topic {i+1} Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(topic["level"]), key=f"edit_topic_{i}_level") for i, topic in enumerate(profile_data["topics_to_learn"])]


                    submitted = st.form_submit_button("💾 Save Changes")
                    if submitted:
                        updated_data = {
                            "name": st.session_state.edit_name,
                            "email": st.session_state.edit_email,
                            "age": st.session_state.edit_age,
                            "phone": st.session_state.edit_phone,
                            "learning_goal": {
                                "goal": st.session_state.edit_goal,
                                "desired_proficiency": st.session_state.edit_goal_proficiency
                            },
                            "skills": [{"name": n, "level": l} for n, l in zip(skills, skill_levels)],
                            "topics_to_learn": [{"name": n, "level": l} for n, l in zip(topics, topic_levels)]
                        }
                        # Save updated_data to DB here
                        st.success("✅ Profile updated!")
                        st.session_state.edit_mode = False
                        # st.rerun()
            else:
                st.markdown(f"**Name:** {profile_data['name']}")
                st.markdown(f"**Email:** {profile_data['email']}")
                st.markdown(f"**Age:** {profile_data['age']}")
                st.markdown(f"**Phone:** {profile_data['phone']}")

                st.subheader("Skills")
                for skill in profile_data["skills"]:
                    st.markdown(f"- {skill['name']} ({skill['level']})")

                st.subheader("Learning Goal")
                st.markdown(f"**Goal:** {profile_data['learning_goal']['goal']}")
                st.markdown(f"**Desired Proficiency:** {profile_data['learning_goal']['desired_proficiency']}")

                st.subheader("Topics to Learn")
                for topic in profile_data["topics_to_learn"]:
                    st.markdown(f"- {topic['name']} ({topic['level']})")

                st.button("✏️ Edit Profile", on_click=lambda: setattr(st.session_state, "edit_mode", True))

    # --- RIGHT PANE: Recommendations ---
    with col2:
        st.subheader("🔍 Study Material Recommendations")

        conn = sqlite3.connect("user_data.db")
        try:
            # Get user ID
            user_df = pd.read_sql_query("SELECT id FROM User WHERE name = 'Sinegalatha B';", conn)
            if not user_df.empty:
                user_id = user_df["id"].values[0]

                # --- Learning Goals ---
                st.markdown("### 🎯 Learning Goals")
                goal_df = pd.read_sql_query(f"SELECT goal_name, goal_proficiency FROM LearningGoal WHERE user_id = '{user_id}';", conn)
                if not goal_df.empty:
                    for _, row in goal_df.iterrows():
                        goal_name = row["goal_name"]
                        goal_proficiency = row["goal_proficiency"]
                        st.markdown(f"**{goal_name}** ({goal_proficiency})")
                        with st.spinner(f"Getting resources for {goal_name}..."):
                            try:
                                rec = recommendationTool(goal_name, goal_proficiency)
                                st.markdown(rec)
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.info("No learning goals found.")

                # --- Topics ---
                st.markdown("### 📚 Topics to Learn")
                topic_df = pd.read_sql_query(f"SELECT topic_name, topic_proficiency FROM Topic WHERE user_id = '{user_id}';", conn)
                if not topic_df.empty:
                    for _, row in topic_df.iterrows():
                        topic_name = row["topic_name"]
                        topic_proficiency = row["topic_proficiency"]
                        st.markdown(f"**{topic_name}** ({topic_proficiency})")
                        with st.spinner(f"Getting resources for {topic_name}..."):
                            try:
                                rec = recommendationTool(topic_name, topic_proficiency)
                                st.markdown(rec)
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.info("No topics found.")
            else:
                st.warning("User Sinegalatha B not found in database.")
        except Exception as e:
            st.error(f"❌ Database error: {e}")
        finally:
            conn.close()
# with tabs[3]:  # Admin tab
#     st.header("👨‍💼 Admin Panel")
#     admin_view = st.radio("Select Admin Function", ["Register Profiles", "Profile-Based Recommendations"], horizontal=True)

#     if admin_view == "Register Profiles":
#         st.subheader("📝 Register Profile")

#         # Basic Details
#         name = st.text_input("Name", key="name_input")
#         email = st.text_input("Email", key="email_input")
#         age = st.number_input("Age", min_value=0, step=1, key="age_input")
#         phone = st.text_input("Phone Number", key="phone_input")

#         # Skills Section
#         st.subheader("Skills")
#         for i, skill in enumerate(st.session_state.skills):
#             st.text_input(f"Skill #{i+1} Name", value=skill['name'], key=f'skill_name_{i}')
#             st.selectbox(
#                 f"Skill #{i+1} Proficiency",
#                 ["Beginner", "Intermediate", "Advanced"],
#                 index=["Beginner", "Intermediate", "Advanced"].index(skill['level']),
#                 key=f'skill_level_{i}'
#             )

#         # Add Skill Form
#         with st.form("add_skill_form", clear_on_submit=True):
#             if st.form_submit_button("➕ Add Skill"):
#                 st.session_state.skills.append({'name': '', 'level': 'Beginner'})

#         # Learning Goal Section
#         st.subheader("Learning Goal")
#         learning_goal = st.text_input("Goal", key="goal_input")
#         goal_proficiency = st.selectbox(
#             "Desired Proficiency",
#             ["Beginner", "Intermediate", "Advanced"],
#             key="goal_proficiency_input"
#         )

#         # Topics Section
#         st.subheader("Topics to Learn")
#         for i, topic in enumerate(st.session_state.topics):
#             st.text_input(f"Topic #{i+1} Name", value=topic['name'], key=f'topic_name_{i}')
#             st.selectbox(
#                 f"Topic #{i+1} Proficiency",
#                 ["Beginner", "Intermediate", "Advanced"],
#                 index=["Beginner", "Intermediate", "Advanced"].index(topic['level']),
#                 key=f'topic_level_{i}'
#             )

#         # Add Topic Form
#         with st.form("add_topic_form", clear_on_submit=True):
#             if st.form_submit_button("➕ Add Topic"):
#                 st.session_state.topics.append({'name': '', 'level': 'Beginner'})

#         # Submit Full Form
#         with st.form("signup_form"):
#             submitted = st.form_submit_button("✅ Submit")
#             if submitted:
#                 skills_final = []
#                 for i in range(len(st.session_state.skills)):
#                     skill_name = st.session_state.get(f'skill_name_{i}', '')
#                     skill_level = st.session_state.get(f'skill_level_{i}', 'Beginner')
#                     if skill_name:
#                         skills_final.append({'name': skill_name, 'level': skill_level})

#                 topics_final = []
#                 for i in range(len(st.session_state.topics)):
#                     topic_name = st.session_state.get(f'topic_name_{i}', '')
#                     topic_level = st.session_state.get(f'topic_level_{i}', 'Beginner')
#                     if topic_name:
#                         topics_final.append({'name': topic_name, 'level': topic_level})

#                 document = {
#                     "name": name,
#                     "email": email,
#                     "age": age,
#                     "phone": phone,
#                     "skills": skills_final,
#                     "learning_goal": {
#                         "goal": learning_goal,
#                         "desired_proficiency": goal_proficiency
#                     },
#                     "topics_to_learn": topics_final
#                 }

#                 save_to_db(document)
#                 st.success("✅ Data submitted and saved successfully!")
#                 time.sleep(2)

#                 # Clear session state
#                 for key in list(st.session_state.keys()):
#                     del st.session_state[key]
#                 # st.rerun()

#     elif admin_view == "Profile-Based Recommendations":
#         st.subheader("📌 Profile-Based Study Recommendations")
#         conn = sqlite3.connect("user_data.db")

#         try:
#             user_df = pd.read_sql_query("SELECT id, name FROM User;", conn)
#             user_names = user_df["name"].tolist()
#             selected_user_name = st.selectbox("Select a User", user_names)

#             if selected_user_name:
#                 user_id = user_df[user_df["name"] == selected_user_name]["id"].values[0]

#                 st.subheader("🎯 Learning Goals Recommendations")
#                 goal_query = f"SELECT goal_name, goal_proficiency FROM LearningGoal WHERE user_id = '{user_id}';"
#                 goal_df = pd.read_sql_query(goal_query, conn)

#                 if not goal_df.empty:
#                     for _, row in goal_df.iterrows():
#                         goal_name = row["goal_name"]
#                         goal_proficiency = row["goal_proficiency"]
#                         st.markdown(f"**{goal_name}** ({goal_proficiency})")
#                         with st.spinner(f"Getting resources for {goal_name}..."):
#                             try:
#                                 rec = recommendationTool(goal_name, goal_proficiency)
#                                 st.markdown(rec)
#                             except Exception as e:
#                                 st.error(f"Error for goal {goal_name}: {e}")
#                 else:
#                     st.info("No learning goals found for this user.")

#                 st.subheader("📚 Topic-Based Recommendations")
#                 topic_query = f"SELECT topic_name, topic_proficiency FROM Topic WHERE user_id = '{user_id}';"
#                 topic_df = pd.read_sql_query(topic_query, conn)

#                 if not topic_df.empty:
#                     for _, row in topic_df.iterrows():
#                         topic_name = row["topic_name"]
#                         topic_proficiency = row["topic_proficiency"]
#                         st.markdown(f"**{topic_name}** ({topic_proficiency})")
#                         with st.spinner(f"Getting resources for {topic_name}..."):
#                             try:
#                                 rec = recommendationTool(topic_name, topic_proficiency)
#                                 st.markdown(rec)
#                             except Exception as e:
#                                 st.error(f"Error for topic {topic_name}: {e}")
#                 else:
#                     st.info("No topics found for this user.")
#         except Exception as e:
#             st.error(f"❌ Database error: {e}")
#         finally:
#             conn.close()
# with tabs[4]:
#     print("TAB4 CLICKED")
#     st.subheader("📌 Profile-Based Study Recommendations")
#     # conn = sqlite3.connect("user_data.db")

#     try:
#         user_df = pd.read_sql_query("SELECT id, name FROM User;", conn)
#         user_names = user_df["name"].tolist()
#         print("*****1",user_names)
#         selected_user_name = st.selectbox("Select a User", user_names)

#         if selected_user_name:
#             print("*****2",selected_user_name)
#             print("*****2",user_df)
#             user_id = user_df[user_df["name"] == selected_user_name]["id"].values[0]
#             print("*****3",user_id)
#             st.subheader("🎯 Learning Goals Recommendations")
#             goal_query = f"SELECT goal_name, goal_proficiency FROM LearningGoal WHERE user_id = '{user_id}';"
#             goal_df = pd.read_sql_query(goal_query, conn)
#             print("*****2",goal_df)
#             goal_df_filtered = goal_df[goal_df["user_id"] == user_id]
#             if not goal_df_filtered.empty:
#                 for _, row in goal_df_filtered.iterrows():
#                     goal_name = row["goal_name"]
#                     goal_proficiency = row["goal_proficiency"]
#                     st.markdown(f"**{goal_name}** ({goal_proficiency})")
#                     with st.spinner(f"Getting resources for {goal_name}..."):
#                         try:
#                             rec = recommendationTool(goal_name, goal_proficiency)
#                             print("*****3",rec)
#                             st.markdown(rec)
#                         except Exception as e:
#                             st.error(f"Error for goal {goal_name}: {e}")
#             else:
#                 st.info("No learning goals found for this user.")

#             st.subheader("📚 Topic-Based Recommendations")
#             topic_query = f"SELECT topic_name, topic_proficiency FROM Topic WHERE user_id = '{user_id}';"
#             topic_df = pd.read_sql_query(topic_query, conn)
#             topic_df_filtered = topic_df[topic_df["user_id"] == user_id]

#             if not topic_df_filtered.empty:
#                 for _, row in topic_df_filtered.iterrows():
#                     topic_name = row["topic_name"]
#                     topic_proficiency = row["topic_proficiency"]
#                     st.markdown(f"**{topic_name}** ({topic_proficiency})")
#                     with st.spinner(f"Getting resources for {topic_name}..."):
#                         try:
#                             rec = recommendationTool(topic_name, topic_proficiency)
#                             st.markdown(rec)
#                         except Exception as e:
#                             st.error(f"Error for topic {topic_name}: {e}")
#             else:
#                 st.info("No topics found for this user.")
#     except Exception as e:
#         st.error(f"❌ Database error: {e}")
#     finally:
#         conn.close()

