from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import tempfile
import os
import streamlit as st

class VectorStore:
    def __init__(self):
        """
        Initialize vector store with HuggingFace embeddings.
        """
        try:
            # Use a lightweight embedding model that works well for document search
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            raise Exception(f"Error initializing embeddings: {str(e)}")
    
    def create_vectorstore(self, documents):
        """
        Create a Chroma vector store from documents.
        
        Args:
            documents (list): List of Document objects
            
        Returns:
            Chroma: Initialized vector store
        """
        if not documents:
            raise ValueError("No documents provided for vector store creation")
        
        try:
            # Create temporary directory for Chroma persistence
            temp_dir = tempfile.mkdtemp()
            
            # Create Chroma vector store
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=temp_dir
            )
            
            return vectorstore
            
        except Exception as e:
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def similarity_search(self, vectorstore, query, k=4):
        """
        Perform similarity search in the vector store.
        
        Args:
            vectorstore: Chroma vector store
            query (str): Search query
            k (int): Number of similar documents to return
            
        Returns:
            list: List of similar documents with metadata
        """
        try:
            # Perform similarity search
            docs = vectorstore.similarity_search(query, k=k)
            return docs
            
        except Exception as e:
            raise Exception(f"Error performing similarity search: {str(e)}")
    
    def similarity_search_with_score(self, vectorstore, query, k=4):
        """
        Perform similarity search with relevance scores.
        
        Args:
            vectorstore: Chroma vector store
            query (str): Search query
            k (int): Number of similar documents to return
            
        Returns:
            list: List of tuples (document, score)
        """
        try:
            # Perform similarity search with scores
            docs_with_scores = vectorstore.similarity_search_with_score(query, k=k)
            return docs_with_scores
            
        except Exception as e:
            raise Exception(f"Error performing similarity search with scores: {str(e)}")
