import openai
import streamlit as st
import os
import pdfplumber
import docx
import pandas as pd
import pptx

# Secure way to use API key
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

st.title("Instructional Design Agent")

# Initialize session state variables
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": "You are an expert instructional design assistant. Your goal is to gather structured information about a course from the user in a natural conversation. Ask intelligent, relevant follow-up questions on the following aspects - topic of the course, audience profile, mode of learning in terms of offline/face-to-face and synchronous/asynchronous, duration, and whether the user has some raw content. Once you have enough details or if the user is not able to provide that information, please stop."},
        {"role": "assistant", "content": "Hope you are having a great day! Looking to build a course today? I can help."}
    ]
if "responses" not in st.session_state:
    st.session_state.responses = []
if "conversation_complete" not in st.session_state:
    st.session_state.conversation_complete = False
if "raw_content" not in st.session_state:
    st.session_state.raw_content = ""
if "content_outline" not in st.session_state:
    st.session_state.content_outline = ""

# Display the latest AI question
latest_message = st.session_state.conversation_history[-1]["content"]
st.write(latest_message)

# User's input
user_response = st.text_input("Your response:", key=str(len(st.session_state.responses)))

# Process the response
if st.button("Next") and user_response:
    st.session_state.responses.append(user_response)
    st.session_state.conversation_history.append({"role": "user", "content": user_response})
    
    # Call OpenAI to get the next question
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=st.session_state.conversation_history + [
            {"role": "system", "content": "Have we gathered enough details? If yes, say 'We seem to have the details we need to get started' and stop asking questions. Otherwise, ask the next relevant question to continue gathering information."}
        ]
    )
    
    # Extract AI's next response
    next_message = response.choices[0].message.content
    st.session_state.conversation_history.append({"role": "assistant", "content": next_message})
    
    # Check if AI decides that enough information is collected
    if "We seem to have the details we need to get started" in next_message:
        st.session_state.conversation_complete = True
    
    st.rerun()

# Once enough context is gathered, display summary before proceeding
if st.session_state.conversation_complete:
    st.write("Here is the summary of the course you are looking to create:")
    summary_prompt = f"""
    Summarize the collected information in a structured format:
    {st.session_state.responses}
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert instructional design assistant. Summarize the collected information in a structured table format for user confirmation."},
            {"role": "user", "content": summary_prompt}
        ]
    )
    summary = response.choices[0].message.content
    st.write(summary)
    
    if st.button("Confirm Summary"):
        st.write("Thanks for sharing all that info! If you have any raw content to upload, please do so below.")
        uploaded_files = st.file_uploader("Upload your course material (PDF, DOCX, TXT, XLSX, PPTX)", accept_multiple_files=True)
    
        raw_text = ""
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        raw_text += text + "\n"
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    raw_text += para.text + "\n"
            elif uploaded_file.type == "text/plain":
                raw_text += uploaded_file.read().decode("utf-8") + "\n"
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                df = pd.read_excel(uploaded_file)
                raw_text += df.to_string() + "\n"
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                ppt = pptx.Presentation(uploaded_file)
                for slide in ppt.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text_frame") and shape.text_frame:
                            for para in shape.text_frame.paragraphs:
                                raw_text += para.text + "\n"
    
        if raw_text:
            st.session_state.raw_content = raw_text
        
        if st.button("Generate Content Outline"):
            gap_analysis_prompt = f"""
            Analyze gaps between the provided raw content and the instructional design context:
            Context:
            {st.session_state.responses}
            Raw Content:
            {st.session_state.raw_content[:2000]}
            """
            
            gap_response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Analyze gaps between user-provided raw content and that which is required to cover the requirements specified in the context."},
                    {"role": "user", "content": gap_analysis_prompt}
                ]
            )
            st.session_state.content_outline = gap_response.choices[0].message.content
            
            st.write("### Generated Content Outline:")
            st.write(st.session_state.content_outline)
            
            modified_outline = st.text_area("Modify the content outline if needed:", st.session_state.content_outline)
            if st.button("Save Outline"):
                st.session_state.content_outline = modified_outline
                st.write("Updated content outline saved!")
