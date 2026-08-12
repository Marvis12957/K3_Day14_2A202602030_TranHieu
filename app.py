import streamlit as st
import time
from domain_assistant import DomainAssistant
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(".env"))

st.set_page_config(page_title="Northstar Student Services", page_icon="🎓", layout="centered")

st.title("🎓 Northstar Student Services Assistant")
st.markdown("Ask me anything about tuition, enrollment, academic policies, or student life!")

@st.cache_resource
def load_assistant():
    return DomainAssistant.from_corpus(corpus_dir="data/student_services", top_k=5)

try:
    assistant = load_assistant()
except Exception as e:
    st.error(f"Failed to load assistant: {e}")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "contexts" in message:
            with st.expander("View Retrieved Contexts"):
                for idx, ctx in enumerate(message["contexts"]):
                    st.markdown(f"**[{idx+1}] {ctx.source_doc}** (Score: {ctx.score:.4f})")
                    st.caption(ctx.text)

# React to user input
if prompt := st.chat_input("What is your question?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            start_time = time.time()
            response = assistant.answer_with_trace(prompt)
            end_time = time.time()
            
            # Display answer
            message_placeholder.markdown(response.actual_answer)
            
            # Display contexts in an expander
            with st.expander(f"View Retrieved Contexts ({len(response.retrieved_chunks)} chunks in {end_time - start_time:.2f}s)"):
                for idx, ctx in enumerate(response.retrieved_chunks):
                    st.markdown(f"**[{idx+1}] {ctx.source_doc}** (Score: {ctx.score:.4f})")
                    st.caption(ctx.text)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response.actual_answer,
                "contexts": response.retrieved_chunks
            })
            
        except Exception as e:
            message_placeholder.error(f"Error generating response: {e}")
