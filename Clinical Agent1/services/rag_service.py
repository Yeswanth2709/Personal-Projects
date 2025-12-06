"""
RAG (Retrieval-Augmented Generation) service.
Manages document indexing and retrieval for clinical knowledge base.
"""
from typing import List, Dict, Any
from pathlib import Path
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from config import KNOWLEDGE_BASE_DIR, VECTOR_STORE_PATH, EMBEDDING_MODEL


class RAGService:
    """Service for document retrieval and RAG operations."""
    
    def __init__(self, knowledge_base_dir: Path = KNOWLEDGE_BASE_DIR):
        self.knowledge_base_dir = knowledge_base_dir
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Create directories if they don't exist
        knowledge_base_dir.mkdir(exist_ok=True)
        VECTOR_STORE_PATH.parent.mkdir(exist_ok=True)
    
    def load_documents(self) -> List[Dict[str, Any]]:
        """Load documents from the knowledge base directory."""
        documents = []
        
        if not self.knowledge_base_dir.exists():
            return documents
        
        # Load all text and markdown files
        for file_path in self.knowledge_base_dir.glob("**/*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append({
                    "content": content,
                    "source": file_path.name,
                    "type": "text"
                })
        
        for file_path in self.knowledge_base_dir.glob("**/*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append({
                    "content": content,
                    "source": file_path.name,
                    "type": "markdown"
                })
        
        return documents
    
    def chunk_documents(self, documents: List[Dict[str, Any]], chunk_size: int = 500) -> List[Dict[str, Any]]:
        """Split documents into smaller chunks for better retrieval."""
        chunks = []
        
        for doc in documents:
            content = doc["content"]
            # Simple chunking by characters
            for i in range(0, len(content), chunk_size):
                chunk_text = content[i:i + chunk_size]
                if chunk_text.strip():
                    chunks.append({
                        "content": chunk_text,
                        "source": doc["source"],
                        "type": doc["type"],
                        "chunk_id": len(chunks)
                    })
        
        return chunks
    
    def index_documents(self, force_reindex: bool = False):
        """Index documents from the knowledge base."""
        index_path = VECTOR_STORE_PATH / "faiss.index"
        docs_path = VECTOR_STORE_PATH / "documents.pkl"
        
        # Load existing index if available and not forcing reindex
        if not force_reindex and index_path.exists() and docs_path.exists():
            self.index = faiss.read_index(str(index_path))
            with open(docs_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
            return
        
        # Load and chunk documents
        raw_documents = self.load_documents()
        if not raw_documents:
            print("No documents found in knowledge base. Creating empty index.")
            # Create empty index
            dimension = 384  # Dimension for all-MiniLM-L6-v2
            self.index = faiss.IndexFlatL2(dimension)
            self.documents = []
            self.metadata = []
            return
        
        chunks = self.chunk_documents(raw_documents)
        self.documents = [chunk["content"] for chunk in chunks]
        self.metadata = [{"source": chunk["source"], "chunk_id": chunk["chunk_id"]} for chunk in chunks]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(self.documents)} chunks...")
        embeddings = self.embedding_model.encode(
            self.documents,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Save index and documents
        VECTOR_STORE_PATH.mkdir(exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        with open(docs_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
        
        print(f"Indexed {len(self.documents)} document chunks.")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant document chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS index
        k = min(top_k, len(self.documents))
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Compile results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append({
                    "content": self.documents[idx],
                    "source": self.metadata[idx]["source"],
                    "distance": float(distance),
                    "relevance_score": 1.0 / (1.0 + float(distance))
                })
        
        return results
    
    def format_context_for_prompt(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into a context string for the LLM."""
        if not retrieved_chunks:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['source']}]\n{chunk['content']}\n"
            )
        
        return "\n".join(context_parts)


# Singleton instance
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """Get or create the RAG service singleton."""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
        _rag_service_instance.index_documents()
    return _rag_service_instance


if __name__ == "__main__":
    # Test the RAG service
    rag = RAGService()
    rag.index_documents(force_reindex=True)
    
    # Test retrieval
    query = "What are the side effects of aspirin?"
    results = rag.retrieve_relevant_chunks(query, top_k=3)
    print(f"\nQuery: {query}")
    print(f"Found {len(results)} relevant chunks:")
    for result in results:
        print(f"\n- Source: {result['source']}")
        print(f"  Relevance: {result['relevance_score']:.3f}")
        print(f"  Content: {result['content'][:100]}...")
