import streamlit as st
import openai
import pandas as pd
import os
import io

# Set your OpenAI API key securely
# It's recommended to use environment variables or Streamlit secrets for API keys
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure you set this environment variable
max_completion_tokens=10000

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
def get_openai_response(prompt, max_completion_tokens=3500):
    try:
        response = openai.ChatCompletion.create(
            model="o1",  # Ensure you have access to GPT-4 or use "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a professional instructional design assistant."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=max_completion_tokens,
            n=1,  # Number of responses to generate
            stop=None  # Define stop sequences if needed
        )
        return response.choices[0].message['content'].strip()
#    except openai.error.OpenAIError as e:
#        st.error(f"OpenAI API returned an error: {e}")
#        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# Step 1: Gather Context Information
def gather_context():
    st.header("Step 1: Gather Course Information")

    if "greeted" not in st.session_state:
        st.session_state.greeted = False
    if not st.session_state.greeted:
        st.write("👋 **Welcome!** How're you doing today? Seems like you are looking to create an e-learning course. Let's work together on it!")
        st.session_state.greeted = True

    if "context" not in st.session_state:
        st.session_state.context = {}
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [
            {"role": "system", "content": (
                "You are an instructional design assistant. Your goal is to collect all essential details such as the topic, audience profile (like age profile, education and experience), key learning outcomes, mode of learning (instructor lead or self paced), duration of the course, whether the user has raw content for the course, and any other information the user has about the context, required to design an e-learning course. "
                "You can ask a maximum of 6 questions so prioritize the questions on its importance. Ask only one question at a time. If the response needs clarification, ask a follow-up. "
                "Once the answer is sufficient, move to the next key topic. Keep the conversation smooth and engaging."
            )}
        ]
    if "current_question" not in st.session_state:
        st.session_state.current_question = "What is the topic of your e-learning course?"
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "context_complete" not in st.session_state:
        st.session_state.context_complete = False

    question_limit = 8  # 6 core + 2 follow-up questions

    if not st.session_state.context_complete:
        st.write(f"**{st.session_state.current_question}**")

        # 🔑 Dynamic key for text input to ensure clearing
        input_key = f"user_input_{len(st.session_state.conversation_history)}"
        user_input = st.text_input("Your Response:", key=input_key)

        if st.button("Submit"):
            if user_input.strip():
                st.session_state.context[st.session_state.current_question] = user_input
                st.session_state.conversation_history.append({"role": "user", "content": user_input})
                st.session_state.question_count += 1

                if st.session_state.question_count >= question_limit:
                    st.session_state.context_complete = True
                else:
                    prompt = (
                        "Here is the conversation so far:\n"
                        + "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.conversation_history])
                        + "\n\nBased on the context gathered, ask the next most relevant question needed to design the course. "
                        "There is a limit of 6 questions, so prioritize the most important ones."
                    )
                    next_question = get_openai_response(prompt)
                    if next_question:
                        st.session_state.current_question = next_question
                        st.session_state.conversation_history.append({"role": "assistant", "content": next_question})
                    else:
                        st.session_state.context_complete = True

                # Force a rerun so the input box gets refreshed
                st.rerun()
            else:
                st.warning("Please enter your response before submitting.")

    if st.session_state.context_complete and "context_summary" not in st.session_state:
    # Generate summarized version with LLM only once
        summary_prompt = (
            "Summarize the following instructional design context into concise bullet points. "
            "Each bullet should have a short label (up to 6 words) representing the key aspect collected, "
            "and a short summary (not the full user response). Avoid repeating full questions or raw text. "
            "Return the result as a two-column table with headers 'Aspect' and 'Summary'.\n\n"
            f"Context:\n{st.session_state.context}"
        )
        summary_result = get_openai_response(summary_prompt)
        st.session_state.context_summary = summary_result

    if st.session_state.context_complete and "context_summary" in st.session_state:
        st.subheader("✅ Summary of Collected Context")
        st.markdown(st.session_state.context_summary)

        cols = st.columns(2)
        with cols[0]:
            if st.button("Approve and Continue"):
                # 🔍 Check for raw content answer before proceeding to Step 2
                has_raw_content = None
                for question, answer in st.session_state.context.items():
                    if "raw content" in question.lower():
                        has_raw_content = "yes" in answer.lower()
                        break
                st.session_state.has_raw_content = has_raw_content

                st.session_state.step = 2
                del st.session_state.context_summary
                st.rerun()
    
        with cols[1]:
            if st.button("Modify Information"):
                st.session_state.context_complete = False
                st.session_state.question_count = 0
                st.session_state.context = {}
                st.session_state.current_question = "What is the topic of your e-learning course?"
                st.session_state.conversation_history = [
                    {"role": "system", "content": st.session_state.conversation_history[0]["content"]}
                ]
                if "context_summary" in st.session_state:
                    del st.session_state.context_summary
                st.rerun()

                # Reset state
                st.session_state.context_complete = False
                st.session_state.question_count = 0
                st.session_state.context = {}
                st.session_state.current_question = "What is the topic of your e-learning course?"
                st.session_state.conversation_history = [
                    {"role": "system", "content": st.session_state.conversation_history[0]["content"]}
                ]
                st.rerun()

# Step 2: Analyze Raw Content
def analyze_content():
    st.header("Step 2: Analyze Raw Content")

    # Upload area
    uploaded_files = st.file_uploader(
        "Upload raw content files (PDF, DOCX, TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        raw_text = ""

        try:
            for uploaded_file in uploaded_files:
                if uploaded_file.type == "application/pdf":
                    from PyPDF2 import PdfReader
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            raw_text += page_text + "\n"
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    import docx
                    doc = docx.Document(uploaded_file)
                    for para in doc.paragraphs:
                        raw_text += para.text + "\n"
                elif uploaded_file.type == "text/plain":
                    raw_text += uploaded_file.getvalue().decode("utf-8") + "\n"
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            return

        st.session_state.raw_text = raw_text

        # Prompt stays as-is
        prompt = (
            f"Analyze the following course objectives and topic:\n"
            f"**Topic:** {st.session_state.context.get('topic')}\n"
            f"**Objectives:** {st.session_state.context.get('objectives')}\n\n"
            f"Here is the raw content:\n{raw_text}\n\n"
            f"Identify any content gaps in the raw content based on the provided topic and objectives."
            f" List the missing topics or areas that need to be covered in the course."
        )

        analysis = get_openai_response(prompt)
        st.session_state.analysis = analysis

        # Show results
        st.subheader("Content Gap Analysis")
        st.write(analysis)

        # Let user choose what to do
        decision = st.radio("How would you like to address the content gaps?", 
                            ("Generate content to fill gaps", "Provide additional sources", "No action needed"))

        if decision == "Generate content to fill gaps":
            filled_prompt = (
                f"Based on the identified content gaps below, generate the necessary content to fill these gaps.\n\n"
                f"**Content Gaps:**\n{analysis}\n\n"
                f"Provide the additional content required to cover these areas effectively."
            )
            filled_content = get_openai_response(filled_prompt)
            if filled_content:
                st.session_state.filled_content = filled_content
                st.success("Content gaps have been filled with generated material.")
                if st.button("Continue to Step 3"):
                    st.session_state.step = 3
                    st.rerun()

        elif decision == "Provide additional sources":
            more_files = st.file_uploader(
                "Upload additional files to improve coverage", 
                type=["pdf", "docx", "txt"], 
                accept_multiple_files=True, 
                key="more_sources"
            )
            if more_files:
                uploaded_files.extend(more_files)
                st.warning("Please click the 'Analyze Again' button below to include the new files.")
                if st.button("Analyze Again"):
                    st.rerun()

        elif decision == "No action needed":
            if st.button("Continue to Step 3"):
                st.session_state.step = 3
                st.rerun()

    else:
        st.info("Please upload at least one raw content file to begin analysis.")



# Step 3: Generate Content Outline
def generate_outline():
    st.header("Step 3: Generate Content Outline")

    prompt = (
        f"Based on the following context information and raw content, generate a detailed content outline for the e-learning course.\n\n"
        f"**Context Information:**\n"
        f"**Topic:** {st.session_state.context.get('topic')}\n"
        f"**Audience Profile:** {st.session_state.context.get('audience_profile')}\n"
        f"**Objectives:** {st.session_state.context.get('objectives')}\n"
        f"**Duration:** {st.session_state.context.get('duration')}\n"
        f"**Graded Final Assessment:** {st.session_state.context.get('graded_assessment')}\n"
        f"**Additional Information:** {st.session_state.context.get('additional_info')}\n\n"
    )

    if st.session_state.raw_content:
        prompt += "Ensure that the content outline heavily incorporates the provided raw content.\n"

    if st.session_state.content_outline is None:
        outline = get_openai_response(prompt)
        if outline:
            st.session_state.content_outline = outline

    st.write("### Generated Content Outline:")
    st.write(st.session_state.content_outline)

    cols = st.columns(2)
    with cols[0]:
        if st.button("Approve Outline and Continue"):
            st.session_state.step = 4
    with cols[1]:
        if st.button("Modify Outline"):
            st.warning("Modification functionality not implemented in this prototype.")
                # Implement modification logic as needed

# Step 4: Generate Storyboard
def generate_storyboard():
    st.header("Step 4: Generate Storyboard")

    prompt = (
        f"Create a storyboard for the e-learning course based on the following content outline and context information.\n\n"
        f"**Content Outline:**\n{st.session_state.content_outline}\n\n"
        f"**Context Information:**\n"
        f"**Topic:** {st.session_state.context.get('topic')}\n"
        f"**Audience Profile:** {st.session_state.context.get('audience_profile')}\n"
        f"**Objectives:** {st.session_state.context.get('objectives')}\n"
        f"**Duration:** {st.session_state.context.get('duration')}\n"
        f"**Graded Final Assessment:** {st.session_state.context.get('graded_assessment')}\n"
        f"**Additional Information:** {st.session_state.context.get('additional_info')}\n\n"
        f"Strictly format the storyboard as a table with three columns: **Onscreen Text**, **Voice Over Script**, **Visualization Guidelines**."
        f"Make sure that the **Onscreen Text** column in the table is NOT the slide title, but should contain key points that help convey the message of the slide. The **Voice Over Script** column should contain the entire narrative voice over covering the content that will be explained in the slide. Give higher priority to user uploaded raw content. Don't make it too generic and keep it focused. Ensure a consistent flow, organize information into interactivities where necessary, and include knowledge checks after every logical chunk of content coverage."
          "\n\nIMPORTANT: Provide the storyboard strictly as a CSV formatted table with exactly three columns: "
          "'Onscreen Text','Voice Over Script','Visualization Guidelines'."
        )

    storyboard = get_openai_response(prompt, max_completion_tokens=20000)
    if storyboard:
        st.session_state.storyboard = storyboard
        st.write("### Generated Storyboard:")

        try:
            df_storyboard = pd.read_csv(io.StringIO(storyboard))
            st.dataframe(df_storyboard)
        except Exception as e:
            st.error(f"Parsing failed: {e}")
            st.write("Raw CSV output below:")
            st.code(storyboard)

        cols = st.columns(2)
        with cols[0]:
            if st.button("Approve Storyboard and Continue"):
                st.session_state.step = 5
        with cols[1]:
            if st.button("Modify Storyboard"):
                st.warning("Modification functionality not implemented in this prototype.")

# Step 5: Create Final Assessment
def create_final_assessment():
    st.header("Step 5: Create Final Assessment")

    if st.session_state.context.get("graded_assessment", "").lower() == "yes":
        prompt = (
            f"Based on the following content outline, create a set of medium-difficulty questions for the final assessment of the e-learning course.\n\n"
            f"**Content Outline:**\n{st.session_state.content_outline}\n\n"
            f"Ensure that the questions accurately reflect the material covered and effectively evaluate the learners' understanding."
        )

        assessment = get_openai_response(prompt, max_tokens=1500)
        if assessment:
            st.session_state.final_assessment = assessment
            st.write("### Final Assessment Questions:")
            st.markdown("```")
            st.write(assessment)
            st.markdown("```")

            cols = st.columns(2)
            with cols[0]:
                if st.button("Approve Assessment"):
                    st.success("Instructional design process completed successfully!")
            with cols[1]:
                if st.button("Modify Assessment"):
                    st.warning("Modification functionality not implemented in this prototype.")
                    # Implement modification logic as needed
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
