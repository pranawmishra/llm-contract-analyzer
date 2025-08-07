from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from langchain_chroma import Chroma
from langchain_voyageai import VoyageAIEmbeddings
from langchain_core.documents import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain_voyageai import VoyageAIRerank
from app.services.langchain_services import ScoredRetriever
import json
from uuid import uuid4
import time

class SemanticSearchRoutes:
    def __init__(self):
        self.embeddings = VoyageAIEmbeddings(
            model="voyage-3-large",
            output_dimension=1024
        )
        self.reranker = VoyageAIRerank(
            model="rerank-2.5", top_k=5
        )

        self.router = APIRouter()

        self._add_routes()

    def _add_routes(self):
        self.router.post("/create-embeddings")(self.create_embeddings)
        self.router.post("/search/{query}")(self.search)

    def create_embeddings(self):
        try:

            t1 = time.perf_counter()

            print("Creating embeddings...")

            vector_store = Chroma(
                collection_name="contracts",
                embedding_function=self.embeddings,
                persist_directory="app/data/chroma_langchain_db",
            )

            with open("output/final_output.json", "r") as f:
                clauses = json.load(f)

            documents = []
            for document in clauses:
                termination_clause = document["termination_clause"]
                confidentiality_clause = document["confidentiality_clause"]
                liability_clause = document["liability_clause"]

                if termination_clause != "Not found":
                    documents.append(
                        Document(
                            page_content=termination_clause, 
                            metadata={
                                "contract_id": document["contract_id"],
                                "clause_type": "termination"
                            }
                        )
                    )

                if confidentiality_clause != "Not found":
                    documents.append(
                        Document(
                            page_content=confidentiality_clause, 
                            metadata={
                                "contract_id": document["contract_id"],
                                "clause_type": "confidentiality"
                            }
                        )
                    )

                if liability_clause != "Not found":
                    documents.append(
                        Document(
                            page_content=liability_clause, 
                            metadata={
                                "contract_id": document["contract_id"],
                                "clause_type": "liability"
                            }
                        )
                    )

            uuids = [str(uuid4()) for _ in range(len(documents))]

            vector_store.add_documents(documents, ids=uuids)

            t2 = time.perf_counter()
            print(f"Time taken: {t2 - t1} seconds")

            return JSONResponse(content={"message": "Embeddings created successfully", "time_taken": t2 - t1})
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return JSONResponse(content={"error": "Error creating embeddings"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def search(self, query: str):
        try:

            t1 = time.perf_counter()

            if not query:
                return JSONResponse(content={"error": "Query is required"}, status_code=status.HTTP_400_BAD_REQUEST)

            vector_store = Chroma(
                collection_name="contracts",
                embedding_function=self.embeddings,
                persist_directory="app/data/chroma_langchain_db",
            )

            # Create a retriever that returns the top 5 results
            retriever = ScoredRetriever(vector_store=vector_store)
            # vector_store.similarity_search_with_relevance_scores

            # Create a Reranker that reranks the top 5 results
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=self.reranker, base_retriever=retriever
            )

            # Invoke the compression retriever
            results = compression_retriever.invoke(query)

            documents = [(res.page_content, res.metadata["similarity_score"]) for res in results]

            return JSONResponse(content={"documents": documents, "query": query, "time_taken": time.perf_counter() - t1})
        except Exception as e:
            print(f"Error searching: {e}")
            return JSONResponse(content={"error": "Error searching"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
