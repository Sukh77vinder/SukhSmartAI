import streamlit as st
from google import genai
from google.genai import types

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="SukhSmart AI", page_icon="🤖", layout="centered")
st.title("🤖 SukhSmart AI")
st.caption("Powered by Google Gemini • Built by You")

# --- 2. SECURE API KEY LOADER ---
# This looks for your key in the hidden secrets file first.
# If it can't find it, it shows a text box as a backup.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    key_status = "✅ API Key loaded securely!"
except (KeyError, FileNotFoundError):
    api_key = st.text_input("Enter your Google API Key:", type="password")
    key_status = "⚠️ Please paste your API key above."

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Settings")
    st.info(key_status)
    
    # A handy button to clear the conversation
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 4. INITIALIZE CHAT MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. DISPLAY OLD MESSAGES ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. HANDLE NEW CHAT INPUT ---
if prompt := st.chat_input("Ask me anything..."):
    
    # Add user message to screen and memory
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if we have an API key before trying to talk to Google
    if not api_key:
        st.error("Please enter your Google API Key in the sidebar to the left!")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Connect to Google
                    client = genai.Client(api_key=api_key.strip())
                    
                    # Format the history perfectly for Google's SDK
                    history = []
                    for msg in st.session_state.messages[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        history.append(
                            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                        )
                    
                    # --- THE FALLBACK SYSTEM ---
                    # If the first model is busy (503) or dead (404), it tries the next one.
                    models_to_try = [
                        "gemini-2.0-flash",       # Fast and smart
                        "gemini-2.0-flash-lite",  # Ultra-fast backup
                        "gemini-4-carbon.5"        # Older stable backup
                    ]
                    
                    response_text = None
                    last_error = None

                    for model_name in models_to_try:
                        try:
                            chat = client.chats.create(model=model_name, history=history)
                            response = chat.send_message(prompt)
                            response_text = response.text
                            break # If it works, stop trying and move on!
                        except Exception as e:
                            last_error = e
                            error_str = str(e)
                            # If the server is busy or the model is missing, try the next one
                            if "503" in error_str or "UNAVAILABLE" in error_str or "404" in error_str:
                                continue 
                            else:
                                raise e # If it's a bad API key, stop immediately

                    # Display the result
                    if response_text:
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        st.error(f"All Google models are busy right now. Please try again in a minute. \n\n*(Tech details: {last_error})*")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
