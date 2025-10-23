# AI PDF Chatbot

An intelligent chatbot built with Streamlit, LangChain, and Google Gemini AI that allows you to upload PDF documents and ask questions based on their content.

## Features

- **PDF Upload**: Upload single or multiple PDF files
- **Text Extraction**: Automatically extracts text from uploaded PDFs
- **Smart Chunking**: Splits documents into optimized chunks for better context retrieval
- **Vector Search**: Uses Chroma vector database with Google Gemini embeddings for semantic search
- **AI-Powered Answers**: Leverages Google Gemini AI to provide accurate, context-aware responses
- **Source Citations**: Shows which PDF and page the answer came from
- **Clean UI**: Simple, intuitive Streamlit interface for easy interaction

## Tech Stack

- **Python 3.11**
- **Streamlit**: Web interface
- **LangChain**: Document processing and orchestration
- **Chroma**: Vector database for semantic search
- **PyPDF2**: PDF text extraction
- **Google Gemini AI**: Embeddings and text generation
- **langchain-google-genai**: Gemini integration for LangChain

## Setup Instructions

### 1. Get Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy the generated API key

### 2. Add API Key to Replit

Your Gemini API key has already been added to Replit Secrets and is available as an environment variable `GEMINI_API_KEY`.

## How to Use

1. **Upload PDFs**:
   - Use the sidebar to upload one or more PDF files
   - The app will automatically extract and process the text
   - You'll see a confirmation with the number of chunks created

2. **Ask Questions**:
   - Type your question in the chat input at the bottom
   - The AI will search through your uploaded documents
   - You'll receive an answer based only on the PDF content

3. **View Sources**:
   - Expand the "Sources" section to see which PDF and page the answer came from
   - This helps verify the information and find more details

4. **Clear Chat**:
   - Use the "Clear Chat History" button in the sidebar to start a new conversation

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── pdf_processor.py       # PDF text extraction and chunking
├── vector_store.py        # Chroma vector database management
├── chat_handler.py        # Gemini AI chat integration
├── .streamlit/
│   └── config.toml       # Streamlit server configuration
├── pyproject.toml        # Python dependencies
└── README.md             # This file
```

## How It Works

1. **Document Processing**:
   - PDFs are uploaded via the Streamlit interface
   - PyPDF2 extracts text from each page
   - Text is split into chunks with overlap for better context

2. **Embedding & Storage**:
   - Document chunks are embedded using Google Gemini embeddings (768 dimensions)
   - Embeddings are stored in a Chroma vector database
   - Each chunk retains metadata (filename, page number)

3. **Question Answering**:
   - User questions are embedded using the same model
   - Similarity search retrieves the most relevant chunks
   - Google Gemini generates an answer based only on retrieved context
   - Source information is displayed alongside the answer

## Configuration

The application uses the following default settings:

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Embedding Model**: `models/gemini-embedding-001`
- **LLM Model**: `gemini-2.5-flash`
- **Temperature**: 0.1 (for consistent responses)
- **Max Output Tokens**: 1000
- **Similarity Search Results**: Top 4 most relevant chunks

## Limitations

- Only processes PDF files (not DOCX, TXT, or other formats)
- Answers are limited to information in the uploaded PDFs
- Best for text-based PDFs (may struggle with image-heavy or scanned documents)
- Requires internet connection for Gemini API

## Tips for Best Results

1. **Upload Clear PDFs**: Text-based PDFs work better than scanned images
2. **Ask Specific Questions**: More specific questions get better answers
3. **Upload Relevant Documents**: Only upload PDFs related to your questions
4. **Check Sources**: Always verify answers by checking the cited sources

## Running Locally

The application is configured to run on Replit, but if you want to run it locally:

```bash
# Install dependencies
pip install streamlit langchain langchain-community langchain-google-genai chromadb PyPDF2

# Set your API key
export GEMINI_API_KEY="your-api-key-here"

# Run the app
streamlit run app.py --server.port 5000
```

## Troubleshooting

**No text extracted from PDF**: 
- Ensure the PDF contains selectable text (not just images)
- Try a different PDF file

**API Key Error**:
- Verify your Gemini API key is correctly set in Replit Secrets
- Check that the key hasn't expired

**Slow responses**:
- Processing large PDFs may take time
- Consider uploading smaller documents or breaking large files into sections

## Future Enhancements

Potential improvements for future versions:

- Support for additional file formats (DOCX, TXT, Markdown)
- Conversation memory to maintain context across questions
- Adjustable chunk size and overlap settings
- Export chat history functionality
- Multi-language support
- Custom embedding model selection

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please refer to the documentation for each component:
- [Streamlit Docs](https://docs.streamlit.io/)
- [LangChain Docs](https://python.langchain.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
