import os
from datetime import datetime

import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Mermaid Chat Interface", layout="wide", initial_sidebar_state="expanded"
)

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "mermaid_code" not in st.session_state:
    st.session_state.mermaid_code = ""
if "text_content" not in st.session_state:
    st.session_state.text_content = ""
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "system_design" not in st.session_state:
    st.session_state.system_design = ""
if "system_requirements" not in st.session_state:
    st.session_state.system_requirements = ""
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

# Sidebar for chat history
with st.sidebar:
    st.title("📜 Chat History")

    if st.button("➕ New Chat", use_container_width=True):
        if st.session_state.current_chat:
            # Save current chat to history
            chat_session = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": st.session_state.current_chat.copy(),
                "preview": st.session_state.current_chat[0][:50] + "..."
                if st.session_state.current_chat
                else "Empty chat",
                "thread_id": st.session_state.thread_id,
                "mermaid_code": st.session_state.mermaid_code,
                "text_content": st.session_state.text_content,
            }
            st.session_state.chat_history.append(chat_session)

        # Reset current chat and generate new thread_id
        st.session_state.current_chat = []
        st.session_state.mermaid_code = ""
        st.session_state.text_content = ""
        st.session_state.thread_id = None
        st.session_state.system_design = ""
        st.session_state.system_requirements = ""
        st.rerun()

    st.divider()

    # Display chat history
    if st.session_state.chat_history:
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 Chat {len(st.session_state.chat_history) - idx}"):
                st.caption(chat["timestamp"])
                st.text(chat["preview"])
                if st.button("Load", key=f"load_{idx}", use_container_width=True):
                    st.session_state.current_chat = chat["messages"].copy()
                    st.session_state.thread_id = chat.get("thread_id")
                    st.session_state.mermaid_code = chat.get("mermaid_code", "")
                    st.session_state.text_content = chat.get("text_content", "")
                    st.rerun()
    else:
        st.info("No previous chats")

# Main content area
st.title("🤖 Mermaid Chat Interface")

# Check if there are any messages
has_messages = len(st.session_state.current_chat) > 0

if has_messages:
    # Split view: two columns
    col1, col2 = st.columns([1, 1])

    with col1:
        # Render Mermaid diagram preview only (no code editor)
        if st.session_state.is_loading:
            with st.spinner("Generating architecture diagram..."):
                st.empty()
        elif st.session_state.mermaid_code:
            mermaid_html = f"""
            <div class="mermaid">
            {st.session_state.mermaid_code}
            </div>
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true }});
            </script>
            """
            st.components.v1.html(mermaid_html, height=500, scrolling=True)
        else:
            st.info("No diagram to display")

    with col2:
        # Text content area - display system design and requirements
        if st.session_state.system_design or st.session_state.system_requirements:
            combined_text = ""
            if st.session_state.system_design:
                combined_text += f"**System Design:**\n{st.session_state.system_design}\n\n"
            if st.session_state.system_requirements:
                combined_text += f"**System Requirements:**\n{st.session_state.system_requirements}"

            st.text_area(
                "Analysis",
                value=combined_text,
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )
        else:
            st.text_area(
                "Text Content",
                value="Waiting for analysis...",
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )

        st.divider()

        # Display chat messages
        chat_container = st.container(height=150)
        with chat_container:
            for message in st.session_state.current_chat:
                st.markdown(f"**You:** {message}")

        # Chat input at the bottom
        if not st.session_state.is_loading:
            chat_input = st.chat_input("Type your message here...")

            if chat_input:
                # Add message to chat
                st.session_state.current_chat.append(chat_input)
                st.session_state.is_loading = True
                st.rerun()

        # Make API call if loading
        if st.session_state.is_loading:
            try:
                # Prepare the request payload
                payload = {
                    "user_input": st.session_state.current_chat[-1],
                    "thread_id": st.session_state.thread_id,
                }

                # Call the backend API
                response = requests.post(BACKEND_URL, json=payload, timeout=60)
                response.raise_for_status()

                # Parse the response
                result = response.json()
                print(result)
                # Update session state with the results
                st.session_state.thread_id = result.get("thread_id")
                st.session_state.mermaid_code = result.get("output_code", "")
                st.session_state.system_design = result.get("output_design", "")
                st.session_state.system_requirements = result.get("output_requirements", "")
                st.session_state.is_loading = False

                st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {str(e)}")
                st.session_state.is_loading = False
                # Remove the last message since it failed
                if st.session_state.current_chat:
                    st.session_state.current_chat.pop()
                st.rerun()
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.session_state.is_loading = False
                if st.session_state.current_chat:
                    st.session_state.current_chat.pop()
                st.rerun()

else:
    # Initial state: single chat prompt
    st.markdown("""
    ### Welcome! 👋
    
    Enter your first message below to start the conversation. Once you send a message, 
    the interface will split into two columns:
    - **Left column:** Mermaid diagram editor and preview
    - **Right column:** Text content area and chat messages
    """)

    # Center the chat input
    st.markdown("<br>" * 3, unsafe_allow_html=True)

    chat_input = st.chat_input("Type your message to begin...")

    if chat_input:
        st.session_state.current_chat.append(chat_input)
        st.session_state.is_loading = True
        st.rerun()

# Footer
st.divider()
st.caption("Built with Streamlit | Mermaid diagrams powered by Mermaid.js")
