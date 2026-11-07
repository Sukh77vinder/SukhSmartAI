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
            client = genai.Client(api_key=api_key.strip())
            
            history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                history.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                )
            
            # THIS IS THE LINE THAT MUST BE CHANGED
            chat = client.chats.create(model="gemini-2.0-flash-lite", history=history)
            
