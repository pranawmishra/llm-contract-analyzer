from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from typing import List, Any
from pydantic import Field


class ScoredRetriever(BaseRetriever):
    vector_store: Any = Field()  # required for LangChain to register the field

    def _get_relevant_documents(self, query: str) -> List[Document]:
        docs, scores = zip(*self.vector_store.similarity_search_with_score(query, k=5))
        for doc, score in zip(docs, scores):
            doc.metadata["similarity_score"] = score
        return list(docs)