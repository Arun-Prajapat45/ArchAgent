import streamlit as st
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Mermaid Chat Interface",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to fix alignment and reduce top padding
st.markdown("""
    <style>
        /* Reduce padding at the top of the main content area */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
        /* Align columns to the very top */
        [data-testid="column"] {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        /* Ensure the mermaid container doesn't have extra top margin */
        .stHtml {
            margin-top: -50px;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = []
if 'mermaid_code' not in st.session_state:
    st.session_state.mermaid_code = ""
if 'text_content' not in st.session_state:
    st.session_state.text_content = ""

# Sidebar for chat history
with st.sidebar:
    st.title("📜 Chat History")
    
    if st.button("➕ New Chat", use_container_width=True):
        if st.session_state.current_chat:
            # Save current chat to history
            chat_session = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'messages': st.session_state.current_chat.copy(),
                'preview': st.session_state.current_chat[0][:50] + "..." if st.session_state.current_chat else "Empty chat"
            }
            st.session_state.chat_history.append(chat_session)
        
        # Reset current chat
        st.session_state.current_chat = []
        st.session_state.mermaid_code = ""
        st.session_state.text_content = ""
        st.rerun()
    
    st.divider()
    
    # Display chat history
    if st.session_state.chat_history:
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 Chat {len(st.session_state.chat_history) - idx}"):
                st.caption(chat['timestamp'])
                st.text(chat['preview'])
                if st.button(f"Load", key=f"load_{idx}", use_container_width=True):
                    st.session_state.current_chat = chat['messages'].copy()
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
        if st.session_state.mermaid_code:
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
        # Text content area
        text_input = st.text_area(
            "Text Content",
            value=st.session_state.text_content,
            height=300,
            placeholder="Additional text content goes here...",
            label_visibility="collapsed"
        )
        
        if text_input != st.session_state.text_content:
            st.session_state.text_content = text_input
        
        st.divider()
        
        # Display chat messages
        chat_container = st.container(height=150)
        with chat_container:
            for idx, message in enumerate(st.session_state.current_chat):
                st.markdown(f"**Message {idx + 1}:** {message}")
        
        # Chat input at the bottom
        chat_input = st.chat_input("Type your message here...")
        
        if chat_input:
            st.session_state.current_chat.append(chat_input)
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
        # Set default mermaid code as example
        st.session_state.mermaid_code = """graph TD
    A[Start] --> B{Question}
    B -->|Yes| C[OK]
    B -->|No| D[End]
    C --> D"""
        st.rerun()

# Footer
st.divider()
st.caption("ArchAgent | by Akshat Sharma")