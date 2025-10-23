import os
from google import genai
from google.genai import types
from vector_store import VectorStore

class ChatHandler:
    def __init__(self, vectorstore):
        """
        Initialize chat handler with Gemini AI client and vector store.
        
        Args:
            vectorstore: Chroma vector store instance
        """
        self.vectorstore = vectorstore
        self.vector_store_helper = VectorStore()
        
        # Initialize Gemini AI client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
    
    def get_response(self, query, k=4):
        """
        Get AI response based on similarity search results.
        
        Args:
            query (str): User question
            k (int): Number of similar documents to retrieve
            
        Returns:
            tuple: (response_text, sources_list)
        """
        try:
            # Perform similarity search
            relevant_docs = self.vector_store_helper.similarity_search(
                self.vectorstore, query, k=k
            )
            
            if not relevant_docs:
                return "I couldn't find any relevant information in the uploaded documents to answer your question.", []
            
            # Prepare context from relevant documents
            context = ""
            sources = []
            
            for doc in relevant_docs:
                context += f"\n--- Source: {doc.metadata.get('filename', 'Unknown')} ---\n"
                context += doc.page_content + "\n"
                
                # Add source information
                source_info = {
                    "filename": doc.metadata.get('filename', 'Unknown'),
                    "page": doc.metadata.get('page', 'Unknown')
                }
                
                # Avoid duplicate sources
                if source_info not in sources:
                    sources.append(source_info)
            
            # Create prompt for Gemini
            system_instruction = """You are a helpful AI assistant that answers questions based solely on the provided document content. 

Instructions:
1. Answer the question using ONLY the information provided in the context below
2. Be concise but comprehensive in your response
3. If the context doesn't contain enough information to answer the question, say so clearly
4. Do not make up information that isn't in the provided context
5. Use a friendly and professional tone
6. Structure your answer clearly with bullet points or numbered lists when appropriate"""

            user_prompt = f"""Context from uploaded documents:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""

            # Generate response using Gemini
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user", 
                        parts=[types.Part(text=user_prompt)]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,  # Lower temperature for more consistent responses
                    max_output_tokens=1000
                )
            )
            
            if response.text:
                return response.text.strip(), sources
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question.", sources
                
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            return error_msg, []
    
    def get_response_with_scores(self, query, k=4, score_threshold=0.5):
        """
        Get AI response with relevance score filtering.
        
        Args:
            query (str): User question
            k (int): Number of similar documents to retrieve
            score_threshold (float): Minimum relevance score
            
        Returns:
            tuple: (response_text, sources_list)
        """
        try:
            # Perform similarity search with scores
            docs_with_scores = self.vector_store_helper.similarity_search_with_score(
                self.vectorstore, query, k=k
            )
            
            # Filter documents by score threshold
            relevant_docs = [
                doc for doc, score in docs_with_scores 
                if score <= score_threshold  # Lower scores mean higher similarity in some implementations
            ]
            
            if not relevant_docs:
                return "I couldn't find sufficiently relevant information in the uploaded documents to answer your question confidently.", []
            
            # Use the regular response method with filtered documents
            context = ""
            sources = []
            
            for doc in relevant_docs:
                context += f"\n--- Source: {doc.metadata.get('filename', 'Unknown')} ---\n"
                context += doc.page_content + "\n"
                
                # Add source information
                source_info = {
                    "filename": doc.metadata.get('filename', 'Unknown'),
                    "page": doc.metadata.get('page', 'Unknown')
                }
                
                # Avoid duplicate sources
                if source_info not in sources:
                    sources.append(source_info)
            
            # Generate response using the context
            system_instruction = """You are a helpful AI assistant that answers questions based solely on the provided document content. 

Instructions:
1. Answer the question using ONLY the information provided in the context below
2. Be concise but comprehensive in your response
3. If the context doesn't contain enough information to answer the question, say so clearly
4. Do not make up information that isn't in the provided context
5. Use a friendly and professional tone
6. Structure your answer clearly with bullet points or numbered lists when appropriate"""

            user_prompt = f"""Context from uploaded documents:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""

            # Generate response using Gemini
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user", 
                        parts=[types.Part(text=user_prompt)]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                    max_output_tokens=1000
                )
            )
            
            if response.text:
                return response.text.strip(), sources
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question.", sources
                
        except Exception as e:
            error_msg = f"Error generating response with scores: {str(e)}"
            return error_msg, []
