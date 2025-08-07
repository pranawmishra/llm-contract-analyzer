from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from langchain_chroma import Chroma
from langchain_voyageai import VoyageAIEmbeddings
from langchain_core.documents import Document
import json
from uuid import uuid4
import time

class SemanticSearchRoutes:
    def __init__(self):
        self.embeddings = VoyageAIEmbeddings(
            model="voyage-3-large",
            output_dimension=1024
        )

        self.router = APIRouter()

        self._add_routes()

    def _add_routes(self):
        self.router.post("/create-embeddings")(self.create_embeddings)
        self.router.post("/search/{query}")(self.search)

    def create_embeddings(self):

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

    def search(self, query: str):

        t1 = time.perf_counter()

        if not query:
            return JSONResponse(content={"error": "Query is required"}, status_code=400)

        vector_store = Chroma(
            collection_name="contracts",
            embedding_function=self.embeddings,
            persist_directory="app/data/chroma_langchain_db",
        )

        results = vector_store.similarity_search(query, k=5)

        documents = [res.page_content for res in results]

        return JSONResponse(content={"documents": documents, "query": query, "time_taken": time.perf_counter() - t1})

