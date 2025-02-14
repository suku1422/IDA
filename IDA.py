import openai
import streamlit as st
import os
from PyPDF2 import PdfReader

# Secure way to use API key (Recommended)
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

st.title("Instructional Design Agent")

# Initialize session state variables
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": "You are an expert instructional design assistant. Your goal is to gather structured information about a course from the user in a natural conversation. Ask intelligent, relevant follow-up questions on the following aspects - topic of the course, audience profile, mode of learning, duration and whether the user has some raw content. Once you have enough details or if the user is not able to provide that information please stop."},
        {"role": "assistant", "content": "Hope you are having a great day! Looking to build a course today? I can help"}
    ]
if "responses" not in st.session_state:
    st.session_state.responses = []
if "conversation_complete" not in st.session_state:
    st.session_state.conversation_complete = False
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "content_extracted" not in st.session_state:
    st.session_state.content_extracted = ""
if "gaps_identified" not in st.session_state:
    st.session_state.gaps_identified = ""
if "outline_generated" not in st.session_state:
    st.session_state.outline_generated = ""

# Display the latest AI question
latest_message = st.session_state.conversation_history[-1]["content"]
st.write(latest_message)

# User's input with a dynamic key to clear the previous response
user_response = st.text_input("Your response:", key=str(len(st.session_state.responses)))

# Process the response
if st.button("Next") and user_response:
    st.session_state.responses.append(user_response)
    st.session_state.conversation_history.append({"role": "user", "content": user_response})
    
    # Call OpenAI to get the next question
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.conversation_history + [
            {"role": "system", "content": "Have we gathered enough details? If yes, say 'We seem to have the details we need to get started' and stop asking questions. Otherwise, ask the next relevant question to continue gathering information."}
        ]
    )
    
    # Extract AI's next response
    next_message = response.choices[0].message.content
    st.session_state.conversation_history.append({"role": "assistant", "content": next_message})
    
    # Check if AI decides that enough information is collected
    st.session_state.conversation_complete = True
    
    # Refresh the page to update the conversation and clear input
    st.rerun()

# Once enough context is gathered, generate the summary
if st.session_state.conversation_complete:
    st.write("Thanks for sharing all that info! Here’s a structured summary:")
    
    summary_prompt = """
    Based on the conversation so far, summarize the key details about the instructional design context in a structured way.
    {}
    """.format(str(st.session_state.responses))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert instructional design assistant. Summarize the collected information strictly in a structured, table format with the information you were looking for and that which has been provided by the user. If the user wants a change, make the change as needed"},
            {"role": "user", "content": summary_prompt}
        ]
    )

    summary = response.choices[0].message.content
    st.write(summary)
    
    # Upload Raw Content
    st.write("Upload supporting documents (PDF, DOCX, TXT, XLS, JPG, PNG):")
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True, type=["pdf", "docx", "txt", "xls", "jpg", "png"])
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        extracted_text = ""
        for uploaded_file in uploaded_files:
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
        st.session_state.content_extracted = extracted_text
        
        # Perform Gap Analysis
        gap_prompt = f"""
        Here is the course summary:
        {summary}
        
        Here is the extracted content:
        {extracted_text}
        
        Identify gaps between the course summary and the extracted content. List missing areas.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an instructional design assistant. Also assume the role of a compassionate expert in the field identified from the conversation history. Identify gaps in the content compared to the course summary."},
                {"role": "user", "content": gap_prompt}
            ]
        )
        
        st.session_state.gaps_identified = response.choices[0].message.content
        st.write("Identified Gaps:")
        st.write(st.session_state.gaps_identified)
        
        # Ask if user wants to upload more docs or fill gaps with AI
        st.write("There are some missing areas in the content.")
        user_choice = st.text_input("Would you like to upload more documents or have AI generate the missing content?")
        
        if user_choice.lower() == "let ai fill the gaps":
            fill_prompt = f"""
            Here are the missing content areas:
            {st.session_state.gaps_identified}
            
            Generate relevant content to fill these gaps in the instructional design context.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer. Generate content to fill the identified gaps."},
                    {"role": "user", "content": fill_prompt}
                ]
            )
            
            generated_content = response.choices[0].message.content
            st.write("AI-Generated Content to Fill Gaps:")
            st.write(generated_content)
            
            # Generate Content Outline
            outline_prompt = f"""
            Here is the final compiled content (original + AI-generated):
            {st.session_state.content_extracted}

{generated_content}
            
            Generate a structured content outline.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer. Generate a structured content outline."},
                    {"role": "user", "content": outline_prompt}
                ]
            )
            
            st.session_state.outline_generated = response.choices[0].message.content
            st.write("Generated Content Outline:")
            st.write(st.session_state.outline_generated)
