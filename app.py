import streamlit as st
from openai import OpenAI

st.title("SukhSmart AI")

# This asks you for your secret key in the sidebar
api_key = st.sidebar.text_input("Enter your Google API Key", type="password")

# This remembers the chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# The chat input box
if prompt := st.chat_input("Ask me anything!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        # Connect to the free Google AI
        client = OpenAI(
            api_key=api_key, 
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        with st.chat_message("assistant"):
            # Get the AI's response from Gemini
            response = client.chat.completions.create(
                model="gemini-2.0-flash", 
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.error("Please enter your API key in the sidebar to the left!")
