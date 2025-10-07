import streamlit as st
from src.openai_client import get_openai_response


def generate_outline( ):
    st.header("Step 3: Generate Content Outline")
    context_summary = st.session_state.get("context_summary_persisted", "")
    analysis = st.session_state.get("analysis", "")
    uploaded_content = st.session_state.get("uploaded_content", "")
    generated_content = st.session_state.get("generated_additional_content", "")

    if not context_summary:
        st.error("Context summary not available. Please complete Step 1.")
        return

    if not uploaded_content and not generated_content:
        st.error("No content available. Please upload content or choose to generate content in Step 2.")
        return

    combined_content = uploaded_content.strip()
    if generated_content:
        combined_content += f"\n\n{generated_content.strip()}"

    if not st.session_state.get("content_outline"):
        prompt = (
            f"Based on the following instructional design context and source content, generate a structured content outline. Make sure that the duration indicated by the user in context_summary_persisted is adhered to when the duration in the outline is generated "
            f"for the e-learning course.\n\n"
            f"### Instructional Design Context:\n{context_summary}\n\n"
            f"### Source Content:\n{combined_content}\n\n"
            f"Present the content outline **strictly** as a table with two columns: Outline | Duration (in mins). Use pipe separators (|) and include a header row. Do not use bullets, dashes, or markdown separators.\n"
            f"Start immediately with the table header. Separate columns using a '|' (pipe symbol).\n"
            f"Do not add bullets or explanations before or after the table."
        )
        with st.spinner("Generating content outline..."):
            outline = get_openai_response(prompt)
            if outline:
                st.session_state.content_outline = outline

    if "content_outline" in st.session_state:
        st.subheader("Generated Content Outline")
        try:
            import pandas as pd
            import io
            df = pd.read_csv(io.StringIO(st.session_state.content_outline), sep="|")

            # Clean headers
            df.columns = [col.strip() for col in df.columns]

            # Drop any unnamed/empty columns
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

            # Reset index to remove auto-numbering from display
            df = df.reset_index(drop=True)
            
            # Retain only the last two columns (in case extra sneaked in)
            if df.shape[1] > 2:
                df = df.iloc[:, -2:]

            # Rename headers to exactly what we want
            df.columns = ["Outline", "Duration (in mins)"]

            # Wrap long text inside cells
            st.markdown(
                """
                <style>
                .stDataFrame td {
                    white-space: pre-wrap !important;
                    word-break: break-word !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Display the table without index
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Could not parse outline as table. Showing raw text.")
            st.code(st.session_state.content_outline)

    with st.form("approve_outline_form"):
        proceed = st.form_submit_button("Approve Outline and Continue", type="primary")
        if proceed:
            st.session_state.step = 4
            st.rerun()