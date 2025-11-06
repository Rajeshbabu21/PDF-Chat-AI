import streamlit as st
import os
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from chat_handler import ChatHandler
from auth import create_user, verify_user
from PIL import Image

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "user" not in st.session_state:
    st.session_state.user = None


def show_snackbar(message: str, type: str = "info", duration: int = 3000):
        
        color = {
                "info": "#2b6cb0",
                "success": "#2f855a",
                "warning": "#975a16",
                "error": "#c53030",
        }.get(type, "#2b6cb0")

        snackbar_id = "snackbar-msg"
        html = f"""
        <div id="{snackbar_id}" style="position:fixed;right:20px;bottom:20px;z-index:9999;">
            <div style="background:{color};color:#fff;padding:12px 18px;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.2);font-family:Arial,Helvetica,sans-serif;">
                {message}
                <span style="margin-left:12px;cursor:pointer;font-weight:bold;" onclick="document.getElementById('{snackbar_id}').style.display='none'">✕</span>
            </div>
        </div>
        <script>
            setTimeout(function() {{
                var el = document.getElementById('{snackbar_id}');
                if (el) el.style.display = 'none';
            }}, {duration});
        </script>
        """
        st.markdown(html, unsafe_allow_html=True)


def show_login_screen():
    # st.title("🔐 Login")
    st.markdown(
        """
        <h1 style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/3064/3064197.png' width='40' height='40'  style="filter: invert(1);">
            Login
        </h1>
        """,
        unsafe_allow_html=True
    )   

    st.write("Please sign in to continue.")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.form("login_form_main"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if verify_user(email, password):
                    st.session_state.user = email
                    st.session_state.page = "home"
                    st.success("Logged in")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        if st.button("Create an account", key="to_signup"):
            st.session_state.page = "signup"
            st.rerun()


def show_signup_screen():
    # st.title("📝 Signup")
    st.markdown(
        """
        <h1 style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
            <i class="fa-solid fa-user-plus" style="font-size: 36px; color: white;"></i>
            Signup
        </h1>
        """,
        unsafe_allow_html=True
    )   
    st.write("Create a new account")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.form("signup_form_main"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            password2 = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create account")
            if submitted:
                if not email or not password:
                    st.error("Email and password required")
                elif password != password2:
                    st.error("Passwords do not match")
                else:
                    ok, msg = create_user(email, password)
                    if ok:
                        st.session_state.user = email
                        st.session_state.page = "home"
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        if st.button("Have an account? Login", key="to_login"):
            st.session_state.page = "login"
            st.rerun()


def main():
    
    st.set_page_config(
        page_title="INTELLIGENT PDF CHATBOT",
        page_icon="📚",
        # page_icon=,
        layout="wide"
    )
    # st.title("📚 AI PDF Chatbot")
    st.markdown(
        """
        <h1 style='display: flex; align-items: center; justify-content: start; gap: 10px;'>
            <i class="fa-solid fa-robot" style="font-size: 36px; color: white;"></i>
            INTELLIGENT PDF CHATBOT
        </h1>
        """,
        unsafe_allow_html=True
    )   
    st.markdown("Upload PDF documents and ask questions based on their content!")

    # Simple router: pages = 'login', 'signup', 'home'
    if "page" not in st.session_state:
        st.session_state.page = "home" if st.session_state.user else "login"

    # Sidebar navigation / logout
    with st.sidebar:
        if st.session_state.user:
            st.write(f"Signed in as **{st.session_state.user}**")
            if st.button("Home", key="nav_home"):
                st.session_state.page = "home"
                st.rerun()
            if st.button("Logout", key="logout"):
                for key in ["user", "messages", "vector_store", "uploaded_files"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.page = "login"
                st.rerun()
        else:
            if st.button("Login", key="nav_login"):
                st.session_state.page = "login"
                st.rerun()
            if st.button("Signup", key="nav_signup"):
                st.session_state.page = "signup"
                st.rerun()

    # Route to the requested page
    if st.session_state.page == "login":
        show_login_screen()
        return
    if st.session_state.page == "signup":
        show_signup_screen()
        return

    # Otherwise treat as home page (protected)
    if not st.session_state.user:
        # if not signed in send to login
        st.session_state.page = "login"
        st.rerun()

    # Check for Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error("⚠️ GEMINI_API_KEY not found in environment variables. Please add your Gemini API key to continue.")
        st.stop()
    
    # Sidebar for file upload
    with st.sidebar:
        # st.header("📁 Upload Documents")
        st.markdown(
            """
            <h2 style='display: flex; align-items: center; justify-content: start; gap: 10px;'>
                <i class="fa-solid fa-folder" style="font-size: 32px; color: white;"></i>
                Upload Documents
            </h2>
            """,
            unsafe_allow_html=True
        )
        
        uploaded_files = st.file_uploader(
            "Choose files (PDF only will be processed)",
            accept_multiple_files=True,
            help="Upload one or more PDF files to chat with their content"
        )

        if uploaded_files:
            # Validate types ourselves so we can show a nicer snackbar
            valid_files = []
            invalid_files = []
            for f in uploaded_files:
                is_pdf = (getattr(f, "type", "") == "application/pdf") or f.name.lower().endswith(".pdf")
                if is_pdf:
                    valid_files.append(f)
                else:
                    invalid_files.append(f.name)

            if invalid_files:
                # Show a snackbar-style error and an inline warning
                show_snackbar(f"Only PDF files are supported. Ignored: {', '.join(invalid_files)}", type="error", duration=6000)
                st.warning(f"Ignored unsupported files: {', '.join(invalid_files)}")

            if not valid_files:
                # Nothing to do when only invalid files were uploaded
                pass
            else:
                # Check if valid files have changed
                current_files = [f.name for f in valid_files]
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

                            for uploaded_file in valid_files:
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
                                st.success(f"✅ Successfully processed {len(valid_files)} PDF(s) into {total_chunks} chunks")

                                # Show file details
                                st.subheader("📄 Processed Files:")
                                for file_name, chunk_count in file_sources.items():
                                    st.write(f"• {file_name}: {chunk_count} chunks")
                            else:
                                st.error("❌ No text could be extracted from the uploaded PDFs")

                        except Exception as e:
                            st.error(f"❌ Error processing PDFs: {str(e)}")
                            st.session_state.vector_store = None
        
        
        if st.button("Clear Chat History", key="clear_chat"):
            if "messages" in st.session_state:
                del st.session_state.messages
            st.rerun()
    
    # Main chat interface
    # st.header("💬 Chat with Your Documents")
    st.markdown(
        """
        <h3 style='display: flex; align-items: center; justify-content: start; gap: 10px; margin-bottom: 10px;'>
            <i class="fa-solid fa-comments" style="font-size: 36px; color: white;"></i>
            Chat with Your Documents
        </h3>
        """,
        unsafe_allow_html=True
    )   
    
    if not st.session_state.vector_store:
        
        st.markdown(
        """
         <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <h5 style='display: flex; align-items: center; justify-content: start; gap: 10px;'>
            <i class="fa-solid fa-hand-point-up" style="font-size: 36px; color: white;"></i>
             Please upload PDF files in the sidebar to start chatting!
        </h5>
        """,
        unsafe_allow_html=True
    )   
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
