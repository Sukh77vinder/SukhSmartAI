import streamlit as st
from google import genai
from google.genai import types

# --- Page Config ---
st.set_page_config(page_title="SukhSmart AI", page_icon="🤖")

st.title("🤖 SukhSmart AI")
st.caption("Powered by Google Gemini")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your Google API Key", type="password")
    
    # A handy button to clear the conversation
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input & Logic ---
if prompt := st.chat_input("Ask me anything!"):
    
    # 1. Add user message to screen and history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Check for API key
    if not api_key:
        st.error("Please enter your Google API Key in the sidebar to the left!")
    else:
        # 3. Generate AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Connect to Google
                    client = genai.Client(api_key=api_key.strip())
                    
                    # Format the chat history for Google
                    history = []
                    for msg in st.session_state.messages[:-1]: # Exclude the current prompt
                        role = "user" if msg["role"] == "user" else "model"
                        history.append(
                            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                        )
                    
                    # 4. FALLBACK LOGIC: If one model is busy, try the next
                    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-8b"]
                    response_text = None
                    last_error = None

                    for model_name in models_to_try:
                        try:
                            chat = client.chats.create(model=model_name, history=history)
                            response = chat.send_message(prompt)
                            response_text = response.text
                            break # If it works, stop trying other models!
                        except Exception as e:
                            last_error = e
                            # If it's a 503 (busy) error, the loop continues to the next model
                            if "503" in str(e) or "UNAVAILABLE" in str(e):
                                continue
                            else:
                                raise e # If it's a different error (like API key issue), stop trying

                    # 5. Display the response
                    if response_text:
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        st.error(f"All models are currently busy. Please try again in a minute. \n\n(Error: {last_error})")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
