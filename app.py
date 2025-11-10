import streamlit as st
import os
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from chat_handler import ChatHandler
from auth import create_user, verify_user
from PIL import Image
import json
from pathlib import Path




_STATE_FILE = Path(__file__).parent / "current_user.json"

def save_current_user(email: str):
    try:
        _STATE_FILE.write_text(json.dumps({"user": email}))
    except Exception:
        pass

def load_current_user():
    try:
        if _STATE_FILE.exists():
            data = json.loads(_STATE_FILE.read_text())
            return data.get("user")
    except Exception:
        pass
    return None

def clear_current_user():
    try:
        if _STATE_FILE.exists():
            _STATE_FILE.unlink()
    except Exception:
        pass


def set_query_user(email: str):
    try:
        
        st.query_params = {"user": email}
    except Exception:
        pass

def clear_query_user():
    try:
        
        st.query_params = {}
    except Exception:
        pass

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "user" not in st.session_state:
    
    try:
        params = st.query_params
        q_user = params.get("user", [None])[0]
    except Exception:
        q_user = None

    st.session_state.user = q_user or load_current_user()

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
   
    st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<h2 style='text-align: center; color: white; display: flex; justify-content: center; align-items: center; gap: 8px;'>
    <span class="material-icons" style="font-size:32px; color:white;">lock</span>
    Login
</h2>
""", unsafe_allow_html=True)

    st.write("Please sign in to continue.")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.form("login_form_main"):
            email = st.text_input("Email",icon=":material/email:")
            password = st.text_input("Password", type="password",icon=":material/lock:")
            submitted = st.form_submit_button("Login",icon=":material/login:")
            if submitted:
                if verify_user(email, password):
                    st.session_state.user = email
                    # persist current user so refresh doesn't log out
                    save_current_user(email)
                    set_query_user(email)
                    st.session_state.page = "home"
                    st.success("Logged in")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        if st.button("Create an account",icon=":material/add:", key="to_signup"):
            st.session_state.page = "signup"
            st.rerun()

def show_signup_screen():
    
    st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<h2 style='text-align: center; color: white; display: flex; justify-content: center; align-items: center; gap: 8px;'>
    <span class="material-icons" style="font-size:32px; color:white;">account_circle</span>
    Signup
</h2>
""", unsafe_allow_html=True)

       
    st.write("Create a new account")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.form("signup_form_main"):
            email = st.text_input("Email",icon=":material/email:")
            password = st.text_input("Password", type="password",icon=":material/lock:")
            password2 = st.text_input("Confirm Password", type="password",icon=":material/lock:")
            submitted = st.form_submit_button("Create account",icon=":material/add:")
            if submitted:
                if not email or not password:
                    st.error("Email and password required")
                elif password != password2:
                    st.error("Passwords do not match")
                else:
                    ok, msg = create_user(email, password)
                    if ok:
                        st.session_state.user = email
                        
                        save_current_user(email)
                        set_query_user(email)
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
        page_icon="robot.png",
        # page_icon=,
        layout="wide"
    )
    
    st.markdown("## :material/robot_2: INTELLIGENT PDF CHATBOT")  
     
    st.markdown("Upload PDF documents and ask questions based on their content!")

    # Simple router: pages = 'login', 'signup', 'home'
    if "page" not in st.session_state:
        st.session_state.page = "home" if st.session_state.user else "login"

    # Sidebar navigation / logout
    with st.sidebar:
        if st.session_state.user:
            st.write(f"Signed in as **{st.session_state.user}**")
            if st.button("Home",icon=":material/home:", key="nav_home"):
                st.session_state.page = "home"
                st.rerun()
            if st.button("Logout", icon=":material/logout:", key="logout"):
                # clear persisted user on logout
                clear_current_user()
                clear_query_user()
                for key in ["user", "messages", "vector_store", "uploaded_files"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.page = "login"
                st.rerun()
        else:
            if st.button("Login",icon=":material/login:", key="nav_login"):
                st.session_state.page = "login"
                st.rerun()
            if st.button("Signup", icon=":material/account_circle:",key="nav_signup"):
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
        st.error("GEMINI_API_KEY not found in environment variables. Please add your Gemini API key to continue.",icon=":material/warning:")
        st.stop()
    
    # Sidebar for file upload
    with st.sidebar:
        st.markdown("""
    <h2 style='display: flex; align-items: center; gap: 10px;'>
        <span class="material-symbols-outlined" style="font-size: 26px;">mail</span>
        Upload Documents
    </h2>

    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
""", unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose files (PDF only will be processed)",
            accept_multiple_files=True,
            help="Upload one or more PDF files to chat with their content"
        )

        if uploaded_files:
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
                                st.success(f"Successfully processed {len(valid_files)} PDF(s) into {total_chunks} chunks",icon=":material/check:")
                                # Show file details
                                
                                st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
<div style="display:flex; align-items:center; gap:8px;">
  <span class="material-symbols-outlined" style="font-size:26px;">
    picture_as_pdf
  </span>
  <h3 style="margin:0;">Processed Files:</h3>
</div>
""", unsafe_allow_html=True)
                                for file_name, chunk_count in file_sources.items():
                                    st.write(f"• {file_name}: {chunk_count} chunks")
                            else:
                                st.error("No text could be extracted from the uploaded PDFs",icon=":material/dangerous:")

                        except Exception as e:
                            st.error(f"Error processing PDFs: {str(e)}",icon=":material/dangerous:")
                            st.session_state.vector_store = None

        if st.button("Clear Chat History", key="clear_chat",icon=":material/delete:"):
            if "messages" in st.session_state:
                del st.session_state.messages
            st.rerun()
    
    
    st.markdown("## :material/chat: Chat with Your Documents") 
    
    if not st.session_state.vector_store:
        # st.markdown("## :material/pan_tool_alt: Chat with Your Documents") 
        st.markdown("""
                    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<h6 style='display: flex; align-items: center; gap: 8px;'>
<span class="material-icons" style="font-size:24px; vertical-align: middle;">pan_tool_alt</span>
Please upload PDF files in the sidebar to start chatting!
</h6>
""", unsafe_allow_html=True)

     
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("Sources",icon=":material/search:"):
                    for source in message["sources"]:
                        st.write(f"• **{source['filename']}** (Page {source.get('page', 'Unknown')})")
    

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
                        with st.expander("Sources",icon=":material/search:"):
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
