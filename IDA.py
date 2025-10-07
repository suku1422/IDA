import logging
import os
from src.auth import process_google_login, get_google_auth_url
from src.db_manager import init_db, get_user_projects
from src.components.context_gatherer import gather_context
from src.components.content_analyzer import analyze_content
from src.components.outline_generator import generate_outline
from src.components.storyboard_generator import generate_storyboard
from src.components.assessment_creator import create_final_assessment
from src.openai_client import model_dict  # Import the model dictionary
import streamlit as st

def main():
    logging.basicConfig(level=logging.INFO)

    # Initialize the database
    # init_db()

    st.session_state.setdefault("user_id", 'test_user')
    st.session_state.setdefault("user_name", 'test_name')
    st.session_state.setdefault("step", 1)
    st.session_state.setdefault("selected_model", "4o-m")  # Default model

    # Main application flow
    if "user_id" not in st.session_state:
        # Handle user authentication
        if "code" in st.query_params:
            st.session_state["state"] = st.query_params.get("state", [""])
            process_google_login(st.query_params)
            st.rerun()
        else:
            st.title("🧠 Instructional Design Agent (IDA)")
            st.write("Please log in with your Google account to continue.")
            auth_url = get_google_auth_url()
            st.markdown(f'''<a href="{auth_url}" target="_self" 
                    style="display: 
                    inline-block; 
                    padding: 12px 24px; 
                    background-color: #4285F4; 
                    color: white; 
                    text-align: center; 
                    text-decoration: none; 
                    font-size: 18px; 
                    border-radius: 8px; 
                    font-weight: bold;">Login with Google</a>''', 
                    unsafe_allow_html=True)
    else:
        st.sidebar.title("ID Vibes")
        st.sidebar.write(f"Logged in as: **{st.session_state['user_name']}**")

        # Add model selector dropdown
        st.sidebar.subheader("Model Selector")
        model_keys = list(model_dict.keys())
        model_labels = [model_dict[key] for key in model_keys]

        # Display the dropdown with labels
        selected_model_label = st.sidebar.selectbox(
            "Choose a model:",
            model_labels,
            index=model_keys.index(st.session_state["selected_model"])
        )

        # Map the selected label back to its corresponding key
        selected_model_key = next(key for key, label in model_dict.items() if label == selected_model_label)
        st.session_state["selected_model"] = selected_model_key

        # Debugging output
        logging.info(f"Selected model: {model_dict[st.session_state['selected_model']]}")

        # Display the selected model
        st.sidebar.write(f"**Selected Model:** {model_dict[st.session_state['selected_model']]}")

        page = st.sidebar.radio("Navigate", ["🛠 IDA Workflow", "📂 My Projects", "➕ Start New Project"])
        
        if page == "🛠 IDA Workflow":
            if st.session_state.step == 1:
                gather_context()
            elif st.session_state.step == 2:
                analyze_content()
            elif st.session_state.step == 3:
                generate_outline()
            elif st.session_state.step == 4:
                generate_storyboard()
            elif st.session_state.step == 5:
                create_final_assessment()
        elif page == "📂 My Projects":
            projects = get_user_projects(st.session_state['user_id'])
            st.write(f"You have {len(projects)} projects.")
            for p in projects:
                st.write(f"- {p[1]}")  # p[1] is the project_title
        elif page == "➕ Start New Project":
            st.write("Start a new project here.")
            new_title = st.text_input("Project Title")

            if st.button("Start Project"):
                if new_title.strip():
                    # Reset session for a fresh workflow
                    st.session_state.step = 1
                    st.session_state.storyboard = None
                    st.session_state.final_assessment = None
                    st.session_state.project_title = new_title.strip()
                    st.success(f"Started new project: {new_title}")
                    st.rerun()
                else:
                    st.warning("Please provide a project title to continue.")

if __name__ == "__main__":
    main()