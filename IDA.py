import openai
import streamlit as st
import os

# Secure way to use API key (Recommended)
api_key = os.getenv("OPENAI_API_KEY")
client = openai.Client(api_key=api_key)

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
        model="gpt-4",
        messages=st.session_state.conversation_history + [
            {"role": "system", "content": "Have we gathered enough details? If yes, say 'We seem to have the details we need to get started' and stop asking questions. Otherwise, ask the next relevant question to continue gathering information."}
        ]
    )
    
    # Extract AI's next response
    next_message = response.choices[0].message.content
    st.session_state.conversation_history.append({"role": "assistant", "content": next_message})
    
    # Check if AI decides that enough information is collected
    if "I have enough details" in next_message:
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
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert instructional design assistant. Summarize the collected information strictly in a structured, table format with the information you were looking for and that which has been provided by the user. If the user wants a change, make the change as needed"},
            {"role": "user", "content": summary_prompt}
        ]
    )

    summary = response.choices[0].message.content
    st.write(summary)
   