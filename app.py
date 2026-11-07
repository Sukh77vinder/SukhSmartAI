import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="SukhSmart AI", page_icon="🤖")
st.title("🤖 SukhSmart AI")
st.caption("Powered by Google Gemini")

# Sidebar for API key and chat controls
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your Google API Key", type="password")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Please enter your Google API Key in the sidebar.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = genai.Client(api_key=api_key.strip())
                    history = []
                    for msg in st.session_state.messages[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        history.append(
                            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                        )
                    
                    # Correct model list based on latest Google AI documentation
                    models_to_try = [
                        "gemini-3.8-flash",        # Primary: Current stable default
                        "gemini-3.5-flash-lite",   # Fallback: Fast and lightweight
                        "gemini-3-flash-preview"   # Extra fallback: Preview model
                    ]
                    response_text = None
                    last_error = None

                    for model_name in models_to_try:
                        try:
                            chat = client.chats.create(model=model_name, history=history)
                            response = chat.send_message(prompt)
                            response_text = response.text
                            break
                        except Exception as e:
                            last_error = e
                            if "503" in str(e) or "UNAVAILABLE" in str(e) or "404" in str(e):
                                continue # If busy or model not found, try the next one
                            else:
                                raise e

                    if response_text:
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        st.error(f"All models are currently busy. Please try again. (Error: {last_error})")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
