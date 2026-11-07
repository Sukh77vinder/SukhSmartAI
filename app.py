import streamlit as st
from google import genai
from google.genai import types

st.title("SukhSmart AI")

api_key = st.sidebar.text_input("Enter your Google API Key", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            # Connect to Google
            client = genai.Client(api_key=api_key.strip())
            
            # Format the history exactly how Google's new SDK requires it
            history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                history.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                )
            
            # Start the chat
            chat = client.chats.create(model="gemini-1.5-flash", history=history)
            response = chat.send_message(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter your API key in the sidebar to the left!")
