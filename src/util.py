import streamlit as st  # Import Streamlit to access session state

def get_selected_model(model_dict):
    # Fetch the selected model from Streamlit session state
    selected_key = st.session_state.get("selected_model", "4o-m")
    model = model_dict.get(selected_key)
    if model is None:
        # Optionally, log a warning here using st.warning or print
        st.warning(f"Selected model '{selected_key}' not found. Falling back to 'gpt-4o-mini'.")
        return "gpt-4o-mini"
    return model