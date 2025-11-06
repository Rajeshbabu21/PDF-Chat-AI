import os
from google.ai import generativelanguage_v1beta as genai
from google.ai.generativelanguage_v1beta import types
from google.api_core import client_options as client_options_lib
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
        
        # Initialize Gemini AI (Generative Language) client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Use API key via client options
        client_opts = client_options_lib.ClientOptions(api_key=api_key)
        self.client = genai.GenerativeServiceClient(client_options=client_opts)
    
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
            
            # Create prompt for Gemini (Generative Language)
            system_instruction = types.Content(parts=[types.Part(text=(
                "You are a helpful AI assistant that answers questions based solely on the provided document content.\n\n"
                "Instructions:\n"
                "1. Answer the question using ONLY the information provided in the context below\n"
                "2. Be concise but comprehensive in your response\n"
                "3. If the context doesn't contain enough information to answer the question, say so clearly\n"
                "4. Do not make up information that isn't in the provided context\n"
                "5. Use a friendly and professional tone\n"
                "6. Structure your answer clearly with bullet points or numbered lists when appropriate"
            ))])

            user_prompt = f"""Context from uploaded documents:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""

            user_content = types.Content(role="user", parts=[types.Part(text=user_prompt)])

            # Build generation config
            gen_config = types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )

            # Normalize model name (GenerativeService expects model names like 'models/xyz')
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            if not model_name.startswith("models/"):
                model_name = f"models/{model_name}"

            # Build request
            request = types.GenerateContentRequest(
                model=model_name,
                system_instruction=system_instruction,
                contents=[user_content],
                generation_config=gen_config,
            )

            # Call the GenerativeService API
            response = self.client.generate_content(request=request)

            # Extract text from the first candidate if present
            if response and response.candidates:
                candidate = response.candidates[0]
                # Join any text parts from the candidate content
                text_parts = []
                if candidate.content and candidate.content.parts:
                    for p in candidate.content.parts:
                        if getattr(p, 'text', None):
                            text_parts.append(p.text)
                response_text = "\n".join(text_parts).strip()
                if response_text:
                    return response_text, sources

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
            system_instruction = types.Content(parts=[types.Part(text=(
                "You are a helpful AI assistant that answers questions based solely on the provided document content.\n\n"
                "Instructions:\n"
                "1. Answer the question using ONLY the information provided in the context below\n"
                "2. Be concise but comprehensive in your response\n"
                "3. If the context doesn't contain enough information to answer the question, say so clearly\n"
                "4. Do not make up information that isn't in the provided context\n"
                "5. Use a friendly and professional tone\n"
                "6. Structure your answer clearly with bullet points or numbered lists when appropriate"
            ))])

            user_prompt = f"""Context from uploaded documents:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""

            user_content = types.Content(role="user", parts=[types.Part(text=user_prompt)])

            # Build generation config
            gen_config = types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )

            # Normalize model name (GenerativeService expects model names like 'models/xyz')
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            if not model_name.startswith("models/"):
                model_name = f"models/{model_name}"

            # Build request
            request = types.GenerateContentRequest(
                model=model_name,
                system_instruction=system_instruction,
                contents=[user_content],
                generation_config=gen_config,
            )

            # Call the GenerativeService API
            response = self.client.generate_content(request=request)

            # Extract text from the first candidate if present
            if response and response.candidates:
                candidate = response.candidates[0]
                # Join any text parts from the candidate content
                text_parts = []
                if candidate.content and candidate.content.parts:
                    for p in candidate.content.parts:
                        if getattr(p, 'text', None):
                            text_parts.append(p.text)
                response_text = "\n".join(text_parts).strip()
                if response_text:
                    return response_text, sources

            return "I apologize, but I couldn't generate a response. Please try rephrasing your question.", sources
                
        except Exception as e:
            error_msg = f"Error generating response with scores: {str(e)}"
            return error_msg, []
