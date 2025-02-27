### **Script: `instructional_design_agent.py`**

import streamlit as st
import openai
import pandas as pd
import os

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your actual OpenAI API key

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'context' not in st.session_state:
    st.session_state.context = {}
if 'raw_content' not in st.session_state:
    st.session_state.raw_content = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'content_outline' not in st.session_state:
    st.session_state.content_outline = None
if 'storyboard' not in st.session_state:
    st.session_state.storyboard = None
if 'final_assessment' not in st.session_state:
    st.session_state.final_assessment = None

# Function to call OpenAI API
def get_openai_response(prompt, temperature=0.5, max_tokens=1500):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional instructional design assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error communicating with OpenAI API: {e}")
        return None

# Step 1: Gather Context Information
def gather_context():
    st.header("Step 1: Gather Course Information")

    # Define questions based on step
    questions = [
        ("topic", "What is the topic of the e-learning course?"),
        ("audience_profile", "Can you describe the audience profile for this course?"),
        ("objectives", "What are the objectives you aim to achieve with this course?"),
        ("raw_content_available", "Is there any raw content available for this course? (yes/no)"),
        ("duration", "What is the desired duration of the training?"),
        ("graded_assessment", "Do you need a graded final assessment in the course? (yes/no)"),
        ("additional_info", "Is there any other information you'd like the agent to keep in mind (e.g., use of summative or narrative voice-over)?")
    ]

    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0

    if st.session_state.current_question < len(questions):
        key, question = questions[st.session_state.current_question]
        user_input = st.text_input(question, key=key)
        if st.button("Submit"):
            if user_input:
                st.session_state.context[key] = user_input
                st.session_state.current_question += 1
            else:
                st.warning("Please provide an answer before proceeding.")
    else:
        # Check if raw content is available
        if st.session_state.context.get("raw_content_available", "").lower() == "yes":
            upload_raw_content()
        else:
            summarize_context()

def upload_raw_content():
    st.header("Upload Raw Content")
    uploaded_file = st.file_uploader("Upload your raw content files (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file:
        # For simplicity, store the file in session state
        st.session_state.raw_content = uploaded_file
        summarize_context()
    else:
        st.info("Please upload the raw content to proceed.")

def summarize_context():
    st.header("Review and Approve Context Information")

    # Create a DataFrame for tabular display
    context_df = pd.DataFrame(list(st.session_state.context.items()), columns=['Parameter', 'Value'])
    st.table(context_df)

    if st.button("Approve and Continue"):
        st.session_state.step = 2
    if st.button("Modify Information"):
        # Reset to step 1
        st.session_state.step = 1

# Step 2: Analyze Raw Content
def analyze_content():
    st.header("Step 2: Analyze Raw Content")

    if st.session_state.raw_content:
        # Read the raw content
        raw_text = ""
        try:
            if st.session_state.raw_content.type == "application/pdf":
                from PyPDF2 import PdfReader
                reader = PdfReader(st.session_state.raw_content)
                for page in reader.pages:
                    raw_text += page.extract_text()
            elif st.session_state.raw_content.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                import docx
                doc = docx.Document(st.session_state.raw_content)
                for para in doc.paragraphs:
                    raw_text += para.text + "\n"
            elif st.session_state.raw_content.type == "text/plain":
                raw_text = st.session_state.raw_content.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            return

        # Compare with context to find gaps
        prompt = (
            f"Analyze the following course objectives and topic:\n"
            f"Topic: {st.session_state.context.get('topic')}\n"
            f"Objectives: {st.session_state.context.get('objectives')}\n\n"
            f"Here is the raw content:\n{raw_text}\n\n"
            f"Identify any content gaps in the raw content based on the provided topic and objectives."
            f"List the missing topics or areas that need to be covered."
        )

        analysis = get_openai_response(prompt)
        if analysis:
            st.session_state.analysis = analysis
            st.write("### Content Analysis:")
            st.write(analysis)

            decision = st.radio("How would you like to address the content gaps?", ("Generate content to fill gaps", "Provide additional sources", "No action needed"))
            if decision == "Provide additional sources":
                additional_files = st.file_uploader("Upload additional source files", type=["pdf", "docx", "txt"], accept_multiple_files=True)
                if additional_files:
                    # Handle additional uploads as needed
                    st.session_state.raw_content = additional_files  # Simplistic handling
                    st.experimental_rerun()
            elif decision == "No action needed":
                st.session_state.step = 3
            elif decision == "Generate content to fill gaps":
                # Placeholder for content generation
                st.info("Content generation not implemented in this prototype.")
                st.session_state.step = 3

            if st.button("Continue to Step 3"):
                st.session_state.step = 3

    else:
        st.error("No raw content available to analyze.")
        st.session_state.step = 3

# Step 3: Generate Content Outline
def generate_outline():
    st.header("Step 3: Generate Content Outline")

    prompt = (
        f"Based on the following context information and raw content, generate a detailed content outline for the e-learning course.\n\n"
        f"Context Information:\nTopic: {st.session_state.context.get('topic')}\n"
        f"Audience Profile: {st.session_state.context.get('audience_profile')}\n"
        f"Objectives: {st.session_state.context.get('objectives')}\n"
        f"Duration: {st.session_state.context.get('duration')}\n"
        f"Graded Final Assessment: {st.session_state.context.get('graded_assessment')}\n"
        f"Additional Information: {st.session_state.context.get('additional_info')}\n\n"
    )
    if st.session_state.raw_content:
        prompt += "Ensure that the content outline heavily incorporates the provided raw content.\n"

    outline = get_openai_response(prompt)
    if outline:
        st.session_state.content_outline = outline
        st.write("### Generated Content Outline:")
        st.write(outline)

        if st.button("Approve Outline and Continue"):
            st.session_state.step = 4
        if st.button("Modify Outline"):
            # Logic for modifying the outline can be added here
            st.warning("Modification functionality not implemented in this prototype.")

# Step 4: Generate Storyboard
def generate_storyboard():
    st.header("Step 4: Generate Storyboard")

    prompt = (
        f"Create a storyboard for the e-learning course based on the following content outline and context information.\n\n"
        f"Content Outline:\n{st.session_state.content_outline}\n\n"
        f"Context Information:\nTopic: {st.session_state.context.get('topic')}\n"
        f"Audience Profile: {st.session_state.context.get('audience_profile')}\n"
        f"Objectives: {st.session_state.context.get('objectives')}\n"
        f"Duration: {st.session_state.context.get('duration')}\n"
        f"Graded Final Assessment: {st.session_state.context.get('graded_assessment')}\n"
        f"Additional Information: {st.session_state.context.get('additional_info')}\n\n"
        f"Format the storyboard as a table with three columns: Onscreen Text, Visualization Guidelines, Voice Over Script. "
        f"Ensure a consistent flow, organize information into interactivities where necessary, and include knowledge checks after every logical chunk of content."
    )

    storyboard = get_openai_response(prompt, max_tokens=2000)
    if storyboard:
        st.session_state.storyboard = storyboard
        st.write("### Generated Storyboard:")
        st.write(storyboard)

        if st.button("Approve Storyboard and Continue"):
            st.session_state.step = 5
        if st.button("Modify Storyboard"):
            # Logic for modifying the storyboard can be added here
            st.warning("Modification functionality not implemented in this prototype.")

# Step 5: Create Final Assessment
def create_final_assessment():
    st.header("Step 5: Create Final Assessment")

    if st.session_state.context.get("graded_assessment", "").lower() == "yes":
        prompt = (
            f"Based on the following content, create a set of medium difficulty questions for the final assessment of the e-learning course.\n\n"
            f"Content:\n{st.session_state.content_outline}\n\n"
            f"Ensure that the questions accurately reflect the material covered and effectively evaluate the learners' understanding."
        )

        assessment = get_openai_response(prompt, max_tokens=1500)
        if assessment:
            st.session_state.final_assessment = assessment
            st.write("### Final Assessment Questions:")
            st.write(assessment)

            if st.button("Approve Assessment"):
                st.success("Instructional design process completed successfully!")
            if st.button("Modify Assessment"):
                # Logic for modifying the assessment can be added here
                st.warning("Modification functionality not implemented in this prototype.")
    else:
        st.success("Instructional design process completed successfully!")

# Main Application Flow
def main():
    st.title("Instructional Design Agent")
    st.write("An interactive agent to help you develop a storyboard for your e-learning course.")

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
    else:
        st.write("Unknown step.")

if __name__ == "__main__":
    main()
