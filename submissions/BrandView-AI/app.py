import streamlit as st
from youtube_agent_team import youtube_team
from mem0 import MemoryClient
import hashlib
import uuid
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="BrandView AI",
    page_icon="images/favicon.png",
    layout="wide"
)

# Initialize mem0 client
client = MemoryClient()

def get_user_id():
    """Generate a unique user ID based on IP address"""
    ip = st.query_params.get("ip", ["unknown"])[0]
    return hashlib.md5(ip.encode()).hexdigest()

def get_all_conversations(user_id):
    """Get all conversations for a user"""
    conversations = client.get_all(user_id=user_id)
    # Group memories by run_id
    conv_dict = {}
    for memory in conversations:
        run_id = memory.get('run_id')
        if run_id:
            if run_id not in conv_dict:
                conv_dict[run_id] = {
                    'messages': [],
                    'created_at': memory.get('created_at', datetime.now().isoformat())
                }
            conv_dict[run_id]['messages'].append(memory)
    return conv_dict

def create_new_conversation():
    """Create a new conversation and return its ID"""
    return str(uuid.uuid4())

def initialize_session_state():
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = create_new_conversation()
        st.session_state.conversations[st.session_state.current_conversation_id] = {
            'messages': [],
            'created_at': datetime.now().isoformat()
        }
    
    # Load existing conversations
    user_id = get_user_id()
    existing_convs = get_all_conversations(user_id)
    st.session_state.conversations.update(existing_convs)

def save_messages_to_memory(messages, is_long_term=False):
    """Save messages to mem0"""
    user_id = get_user_id()
    run_id = st.session_state.current_conversation_id if not is_long_term else None
    client.add(messages, user_id=user_id, run_id=run_id)

def render_sidebar():
    """Render the sidebar with conversation list and new chat button"""
    with st.sidebar:
        st.title("Conversations")
        
        # New chat button - always enabled
        if st.button("New Chat", use_container_width=True):
            st.session_state.current_conversation_id = create_new_conversation()
            st.session_state.conversations[st.session_state.current_conversation_id] = {
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
            st.rerun()
        
        st.divider()
        
        # List of conversations - only show those with messages
        for conv_id, conv_data in st.session_state.conversations.items():
            # Skip empty conversations in the list
            if not conv_data['messages']:
                continue
                
            # Create a unique key for each button
            button_key = f"conv_{conv_id}"
            
            # Format the conversation title (first message)
            first_msg = conv_data['messages'][0].get('content', '')
            title = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
            
            # Style the button based on whether it's the current conversation
            is_current = conv_id == st.session_state.current_conversation_id
            button_style = "primary" if is_current else "secondary"
            
            if st.button(
                title,
                key=button_key,
                use_container_width=True,
                type=button_style
            ):
                st.session_state.current_conversation_id = conv_id
                st.rerun()

def main():
    st.title("BrandView AI")
    
    # Initialize session state and render sidebar
    initialize_session_state()
    render_sidebar()
    
    st.markdown("""
    ### YouTube Influencer Intelligence Agent
    
    I help brands evaluate YouTube creators for influencer marketing by analyzing channels and videos. I can assess audience metrics, brand safety, sponsorship history, and forecast performance to help you make data-driven influencer decisions.
    """)

    # Get current conversation messages
    current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
    messages = current_conv['messages']

    # Display chat messages
    for message in messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        with st.chat_message(role):
            st.markdown(content)

    # Chat input
    if prompt := st.chat_input("What would you like to know about YouTube?"):
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Add user message to chat history
        user_message = {"role": "user", "content": prompt}
        current_conv['messages'].append(user_message)
        save_messages_to_memory([user_message], is_long_term=False)  # Save to long-term memory

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # Get short-term memory context for the team
                    user_id = get_user_id()
                    run_id = st.session_state.current_conversation_id
                    short_term_memories = client.get_all(user_id=user_id, run_id=run_id, page=1, page_size=50)
                    
                    # Update team context with short-term memory
                    if short_term_memories:
                        youtube_team.context = {"memory": short_term_memories}
                    
                    response = youtube_team.run(prompt)
                    st.markdown(response.content)
                    
                    # Add assistant response to chat history
                    assistant_message = {"role": "assistant", "content": response.content}
                    current_conv['messages'].append(assistant_message)
                    save_messages_to_memory([assistant_message], is_long_term=False)  # Save to long-term memory

                    # Show tool calls in expander if available
                    if hasattr(response, 'tool_calls'):
                        with st.expander("Show API calls made"):
                            for call in response.tool_calls:
                                st.json(call)

                    # Show agent interactions in expander if available
                    if hasattr(response, 'members_responses'):
                        with st.expander("Show agent interactions"):
                            for agent, resp in response.members_responses.items():
                                st.markdown(f"*{agent}*")
                                st.markdown(resp.content)
                                st.divider()
                except Exception as e:
                    error_message = f"Analysis failed: {str(e)}"
                    st.error(error_message)
                    error_msg = {"role": "assistant", "content": error_message}
                    current_conv['messages'].append(error_msg)
                    save_messages_to_memory([error_msg], is_long_term=False)  # Save to long-term memory
                
                # Force rerun if this was the first message to update the sidebar
                if len(current_conv['messages']) == 2:  # User message + Assistant response
                    st.rerun()

if __name__ == "__main__":
    main()