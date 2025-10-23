import streamlit as st
import os
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from chat_handler import ChatHandler

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

def main():
    st.set_page_config(
        page_title="AI PDF Chatbot",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 AI PDF Chatbot")
    st.markdown("Upload PDF documents and ask questions based on their content!")
    
    # Check for Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error("⚠️ GEMINI_API_KEY not found in environment variables. Please add your Gemini API key to continue.")
        st.stop()
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload one or more PDF files to chat with their content"
        )
        
        if uploaded_files:
            # Check if files have changed
            current_files = [f.name for f in uploaded_files]
            if current_files != st.session_state.uploaded_files:
                st.session_state.uploaded_files = current_files
                
                with st.spinner("Processing PDFs..."):
                    try:
                        # Initialize processors
                        pdf_processor = PDFProcessor()
                        vector_store = VectorStore()
                        
                        # Process all uploaded files
                        all_documents = []
                        file_sources = {}
                        
                        for uploaded_file in uploaded_files:
                            # Extract text from PDF
                            text = pdf_processor.extract_text(uploaded_file)
                            
                            # Create chunks with metadata
                            chunks = pdf_processor.create_chunks(text, uploaded_file.name)
                            all_documents.extend(chunks)
                            
                            # Store file source mapping
                            file_sources[uploaded_file.name] = len(chunks)
                        
                        if all_documents:
                            # Create vector store
                            vectorstore = vector_store.create_vectorstore(all_documents)
                            st.session_state.vector_store = vectorstore
                            
                            # Display success message
                            total_chunks = len(all_documents)
                            st.success(f"✅ Successfully processed {len(uploaded_files)} PDF(s) into {total_chunks} chunks")
                            
                            # Show file details
                            st.subheader("📄 Processed Files:")
                            for file_name, chunk_count in file_sources.items():
                                st.write(f"• {file_name}: {chunk_count} chunks")
                        else:
                            st.error("❌ No text could be extracted from the uploaded PDFs")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing PDFs: {str(e)}")
                        st.session_state.vector_store = None
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat with Your Documents")
    
    if not st.session_state.vector_store:
        st.info("👆 Please upload PDF files in the sidebar to start chatting!")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📖 Sources"):
                    for source in message["sources"]:
                        st.write(f"• **{source['filename']}** (Page {source.get('page', 'Unknown')})")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    chat_handler = ChatHandler(st.session_state.vector_store)
                    response, sources = chat_handler.get_response(prompt)
                    
                    st.markdown(response)
                    
                    # Display sources if available
                    if sources:
                        with st.expander("📖 Sources"):
                            for source in sources:
                                st.write(f"• **{source['filename']}** (Page {source.get('page', 'Unknown')})")
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "sources": sources
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
