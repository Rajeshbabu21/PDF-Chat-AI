import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import io
import streamlit as st

class PDFProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """
        Initialize PDF processor with text splitter configuration.
        
        Args:
            chunk_size (int): Size of each text chunk
            chunk_overlap (int): Overlap between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text(self, uploaded_file):
        """
        Extract text from uploaded PDF file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text from PDF
        """
        try:
            # Create a BytesIO object from uploaded file
            pdf_bytes = io.BytesIO(uploaded_file.read())
            
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            
            text = ""
            total_pages = len(pdf_reader.pages)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                except Exception as e:
                    st.warning(f"Could not extract text from page {page_num + 1} of {uploaded_file.name}: {str(e)}")
                    continue
            
            if not text.strip():
                raise ValueError(f"No text could be extracted from {uploaded_file.name}")
            
            return text
            
        except Exception as e:
            raise Exception(f"Error extracting text from {uploaded_file.name}: {str(e)}")
    
    def create_chunks(self, text, filename):
        """
        Split text into chunks and create Document objects with metadata.
        
        Args:
            text (str): Text to be chunked
            filename (str): Source filename
            
        Returns:
            list: List of Document objects with metadata
        """
        if not text.strip():
            return []
        
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create Document objects with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Only add non-empty chunks
                    # Extract page number from chunk if available
                    page_num = self._extract_page_number(chunk)
                    
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "filename": filename,
                            "chunk_index": i,
                            "page": page_num
                        }
                    )
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error creating chunks from {filename}: {str(e)}")
    
    def _extract_page_number(self, chunk):
        """
        Extract page number from chunk text.
        
        Args:
            chunk (str): Text chunk
            
        Returns:
            int or str: Page number if found, otherwise "Unknown"
        """
        try:
            # Look for page markers in the text
            lines = chunk.split('\n')
            for line in lines:
                if line.strip().startswith('--- Page ') and line.strip().endswith(' ---'):
                    # Extract page number from marker
                    page_part = line.strip()[9:-4]  # Remove "--- Page " and " ---"
                    return int(page_part)
            return "Unknown"
        except:
            return "Unknown"
