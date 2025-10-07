import streamlit as st
from src.openai_client import get_openai_response

def gather_context():
    # Function to gather context information for instructional design
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
                "You are an instructional design assistant. Your goal is to collect all essential details such as the topic, audience profile (like age profile, education and experience), key learning outcomes, mode of learning (instructor lead or self paced), duration of the course, whether the user has raw content for the course, whether a final assessment and knowledge checks are needed and any other information the user has about the context, required to design an e-learning course. "
                "You can ask a maximum of 7 questions so prioritize the questions on its importance. Ask only one question at a time. If the response needs clarification, ask a follow-up which won't be counted in the 7 questions. "
                "When the user responds to a question, analyze it and see if there is a follow-up question needed to understand the context better. If yes, present that question. Don't ask too many questions but if the user's response is not clear, do not hesitate to ask." 
                "Once the answer is sufficient, move to the next key topic. Keep the conversation smooth and engaging."
            )}
        ]
    if "current_question" not in st.session_state:
        st.session_state.current_question = "What is the topic of your e-learning course?"
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "context_complete" not in st.session_state:
        st.session_state.context_complete = False

    question_limit = 9  # 7 core + 2 follow-up questions

    if not st.session_state.context_complete:
        st.write(f"**{st.session_state.current_question}**")

        # 🔑 Dynamic key for text input to ensure clearing
        input_key = f"user_input_{len(st.session_state.conversation_history)}"
        user_input = st.text_area("Your Response:", key=input_key, height=150)

        if st.button("Submit"):
            if user_input.strip():
                # Process user input and update context
                st.session_state.context[st.session_state.current_question] = user_input
                st.session_state.conversation_history.append({"role": "user", "content": user_input})
                st.session_state.question_count += 1

                # Check if context gathering is complete
                if st.session_state.question_count >= question_limit:
                    st.session_state.context_complete = True
                else:
                    # Update the current question for the next round
                    follow_up_prompt = (
                        "Based on the user's last response, determine if a follow-up question is needed for clarity. "
                        "If yes, provide the follow-up question. If no, provide the next key question needed to gather essential course information. "
                        "Remember, you can ask a maximum of 7 core questions and 2 follow-ups. "
                        "If the limit is reached, respond with 'Context gathering complete.'\n\n"
                        f"Conversation History:\n{st.session_state.conversation_history}\n\n"
                        "What is the next question?"
                    )
                    follow_up_question = get_openai_response(follow_up_prompt)
                    st.session_state.current_question = follow_up_question.strip()
                    st.session_state.conversation_history.append({"role": "assistant", "content": st.session_state.current_question})
                # Clear the input box after submission
                st.rerun()
            else:
                st.warning("Please provide a response before submitting.")

    if st.session_state.context_complete and "context_summary" not in st.session_state:
        # Generate summarized version with LLM only once
        summary_prompt = (
            "Summarize the following instructional design context into concise bullet points. "
            "Each bullet should have a short label (up to 6 words) representing the key aspect collected, "
            "and a short summary (not the full user response). Avoid repeating full questions or raw text. "
            "Return the result as a two-column table with headers 'Aspect' and 'Summary'.\n\n"
            f"Context:\n{st.session_state.context}"
        )
        with st.spinner("Summarizing context..."):
            summary_result = get_openai_response(summary_prompt)
            st.session_state.context_summary = summary_result
            st.session_state.context_summary_persisted = summary_result

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
                    # del st.session_state.context_summary
                    st.rerun()

        with cols[1]:
            if st.button("Modify Information"):
                # Reset context gathering state
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